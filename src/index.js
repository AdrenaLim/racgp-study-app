// RACGP Study System - Cloudflare Worker API
// DB binding: env.DB (D1). Static assets served from ./public via assets binding.

const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
});
const err = (msg, status = 400) => json({ error: msg }, status);

function parseJson(s, fallback) { try { return JSON.parse(s); } catch { return fallback; } }

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;
    const DB = env.DB;
    if (!DB) return err('D1 binding missing', 500);

    // ---------- health ----------
    if (path === '/api/health') {
      const row = await DB.prepare('SELECT COUNT(*) AS n FROM topics').first();
      return json({ ok: true, topics: row?.n ?? 0 });
    }

    // ---------- meta ----------
    if (path === '/api/meta' && method === 'GET') {
      const rows = await DB.prepare('SELECT key, value, source_url, checked_date FROM exam_meta ORDER BY key').all();
      return json(rows.results);
    }

    // ---------- topics ----------
    if (path === '/api/topics' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM topics ORDER BY category, unit, name').all();
      return json(rows.results);
    }
    if (path === '/api/topics' && method === 'POST') {
      const b = await request.json();
      const r = await DB.prepare(
        'INSERT INTO topics (unit, category, name, priority, must_know, should_know, nice_to_know, status, updated_at) VALUES (?,?,?,?,?,?,?,?,date("now"))'
      ).bind(b.unit, b.category, b.name, b.priority, b.must_know || '', b.should_know || '', b.nice_to_know || '', b.status || 'not started').run();
      return json({ ok: true, id: r.meta.last_row_id });
    }
    const topicMatch = path.match(/^\/api\/topics\/(\d+)$/);
    if (topicMatch) {
      const id = +topicMatch[1];
      if (method === 'PUT') {
        const b = await request.json();
        await DB.prepare(
          'UPDATE topics SET unit=?, category=?, name=?, priority=?, must_know=?, should_know=?, nice_to_know=?, status=?, updated_at=date("now") WHERE id=?'
        ).bind(b.unit, b.category, b.name, b.priority, b.must_know || '', b.should_know || '', b.nice_to_know || '', b.status || 'not started', id).run();
        return json({ ok: true });
      }
      if (method === 'DELETE') {
        await DB.prepare('DELETE FROM topics WHERE id=?').bind(id).run();
        return json({ ok: true });
      }
    }

    // ---------- questions ----------
    if (path === '/api/questions' && method === 'GET') {
      const type = url.searchParams.get('type'); // AKT | KFP
      const topic = url.searchParams.get('topic');
      let sql = 'SELECT id, type, topic, unit, stem, options, answers, explanation, pearl, trap FROM questions';
      const conds = [], binds = [];
      if (type) { conds.push('type = ?'); binds.push(type); }
      if (topic) { conds.push('topic = ?'); binds.push(topic); }
      if (conds.length) sql += ' WHERE ' + conds.join(' AND ');
      sql += ' ORDER BY id';
      const rows = await DB.prepare(sql).bind(...binds).all();
      // parse JSON columns client-side-friendly: keep strings; frontend parses
      return json(rows.results);
    }
    if (path === '/api/attempts' && method === 'POST') {
      const b = await request.json(); // { question_id, user_answer, correct }
      await DB.prepare('INSERT INTO attempts (question_id, user_answer, correct, created_at) VALUES (?,?,?,datetime("now"))')
        .bind(b.question_id, JSON.stringify(b.user_answer ?? null), b.correct ? 1 : 0).run();
      return json({ ok: true });
    }

    // ---------- CCE ----------
    if (path === '/api/cce' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM cce_cases ORDER BY id').all();
      return json(rows.results);
    }

    // ---------- guidelines ----------
    if (path === '/api/guidelines' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM guidelines ORDER BY tier, title').all();
      return json(rows.results);
    }

    // ---------- resources ----------
    if (path === '/api/resources' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM resources ORDER BY domain').all();
      return json(rows.results);
    }

    // ---------- rapid sheets ----------
    if (path === '/api/rapid' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM rapid_sheets ORDER BY id').all();
      return json(rows.results);
    }

    // ---------- schedule ----------
    if (path === '/api/schedule' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM schedule ORDER BY week').all();
      return json(rows.results);
    }

    // ---------- mistakes ----------
    if (path === '/api/mistakes' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM mistakes ORDER BY id DESC').all();
      return json(rows.results);
    }
    if (path === '/api/mistakes' && method === 'POST') {
      const b = await request.json();
      await DB.prepare('INSERT INTO mistakes (created_at, exam, topic, question_ref, my_error, correct_principle, why_missed, review_date, status) VALUES (datetime("now"),?,?,?,?,?,?,?,?)')
        .bind(b.exam, b.topic, b.question_ref || '', b.my_error, b.correct_principle, b.why_missed, b.review_date || null, 'open').run();
      return json({ ok: true });
    }
    const mistakeMatch = path.match(/^\/api\/mistakes\/(\d+)$/);
    if (mistakeMatch && method === 'PUT') {
      const b = await request.json();
      await DB.prepare('UPDATE mistakes SET status=?, review_date=? WHERE id=?').bind(b.status, b.review_date || null, +mistakeMatch[1]).run();
      return json({ ok: true });
    }
    if (mistakeMatch && method === 'DELETE') {
      await DB.prepare('DELETE FROM mistakes WHERE id=?').bind(+mistakeMatch[1]).run();
      return json({ ok: true });
    }

    // ---------- reviews (spaced repetition) ----------
    if (path === '/api/reviews' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM reviews ORDER BY due').all();
      return json(rows.results);
    }
    if (path === '/api/reviews' && method === 'POST') {
      const b = await request.json(); // { topic, quality: again|hard|good|easy }
      const INTERVALS = [0, 1, 7, 21, 45, 90]; // days; level maps to interval
      const row = await DB.prepare('SELECT * FROM reviews WHERE topic=?').bind(b.topic).first();
      if (!row) return err('topic not found in reviews', 404);
      let level = row.level;
      if (b.quality === 'again') level = 0;
      else if (b.quality === 'hard') level = Math.max(1, level);
      else if (b.quality === 'good') level = Math.min(5, level + 1);
      else if (b.quality === 'easy') level = Math.min(5, level + 2);
      const interval = INTERVALS[level];
      const due = new Date(Date.now() + interval * 86400000).toISOString().slice(0, 10);
      const streak = (b.quality === 'good' || b.quality === 'easy') ? (row.streak || 0) + 1 : 0;
      await DB.prepare('UPDATE reviews SET level=?, due=?, streak=?, updated_at=date("now") WHERE topic=?')
        .bind(level, due, streak, b.topic).run();
      return json({ ok: true, topic: b.topic, level, due });
    }

    // ---------- dashboard ----------
    if (path === '/api/dashboard' && method === 'GET') {
      const totals = await DB.prepare('SELECT COUNT(*) AS n FROM topics').first();
      const done = await DB.prepare("SELECT COUNT(*) AS n FROM topics WHERE status IN ('learning','solid','exam ready')").first();
      const at = await DB.prepare('SELECT COUNT(*) AS n, SUM(correct) AS c FROM attempts').first();
      const byType = await DB.prepare("SELECT q.type AS type, COUNT(*) AS n, SUM(a.correct) AS c FROM attempts a JOIN questions q ON q.id = a.question_id GROUP BY q.type").all();
      const mistakes = await DB.prepare('SELECT COUNT(*) AS n FROM mistakes WHERE status="open"').first();
      const due = await DB.prepare("SELECT topic FROM reviews WHERE due <= date('now') ORDER BY due").all();
      const weakest = await DB.prepare("SELECT q.topic AS topic, ROUND(100.0*SUM(a.correct)/COUNT(*)) AS pct, COUNT(*) AS n FROM attempts a JOIN questions q ON q.id=a.question_id GROUP BY q.topic HAVING COUNT(*) >= 2 ORDER BY pct ASC LIMIT 5").all();
      const strongest = await DB.prepare("SELECT q.topic AS topic, ROUND(100.0*SUM(a.correct)/COUNT(*)) AS pct, COUNT(*) AS n FROM attempts a JOIN questions q ON q.id=a.question_id GROUP BY q.topic HAVING COUNT(*) >= 2 ORDER BY pct DESC LIMIT 5").all();
      return json({
        topics_total: totals.n, topics_touched: done.n,
        questions_attempted: at.n, questions_correct: at.c ?? 0,
        accuracy: at.n ? Math.round(100 * at.c / at.n) : null,
        by_type: byType.results,
        open_mistakes: mistakes.n,
        due_reviews: due.results.map(r => r.topic),
        weakest: weakest.results, strongest: strongest.results
      });
    }

    // ---------- units (official RACGP curriculum) ----------
    if (path === '/api/units' && method === 'GET') {
      const rows = await DB.prepare('SELECT * FROM units ORDER BY CASE type WHEN "core" THEN 0 ELSE 1 END, number').all();
      return json(rows.results);
    }

    // ---------- notes ----------
    if (path === '/api/notes' && method === 'GET') {
      const unit = url.searchParams.get('unit');
      const topic = url.searchParams.get('topic');
      let sql = 'SELECT * FROM notes'; const conds = []; const binds = [];
      if (unit) { conds.push('unit = ?'); binds.push(unit); }
      if (topic) { conds.push('topic = ?'); binds.push(topic); }
      if (conds.length) sql += ' WHERE ' + conds.join(' AND ');
      sql += ' ORDER BY updated_at DESC';
      const rows = await DB.prepare(sql).bind(...binds).all();
      return json(rows.results);
    }
    if (path === '/api/notes' && method === 'POST') {
      const b = await request.json();
      await DB.prepare('INSERT INTO notes (unit, topic, content, created_at, updated_at) VALUES (?,?,?,datetime("now"),datetime("now"))')
        .bind(b.unit || null, b.topic || null, b.content || '').run();
      return json({ ok: true });
    }
    const noteMatch = path.match(/^\/api\/notes\/(\d+)$/);
    if (noteMatch && method === 'PUT') {
      const b = await request.json();
      await DB.prepare('UPDATE notes SET content=?, updated_at=datetime("now") WHERE id=?').bind(b.content, +noteMatch[1]).run();
      return json({ ok: true });
    }
    if (noteMatch && method === 'DELETE') {
      await DB.prepare('DELETE FROM notes WHERE id=?').bind(+noteMatch[1]).run();
      return json({ ok: true });
    }

    // ---------- 404 ----------
    return err('not found', 404);
  }
};
