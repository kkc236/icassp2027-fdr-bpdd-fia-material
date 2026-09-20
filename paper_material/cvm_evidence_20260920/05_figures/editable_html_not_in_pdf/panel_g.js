/* Native SVG reconstruction of panel (b), at the source's 1448 × 1086 canvas. */
function buildG(d) {
  const c = d.c;
  const sub = (s) => `<tspan baseline-shift="sub" font-size="70%" font-style="${/[a-z]/i.test(s) ? 'italic' : 'normal'}">${s}</tspan>`;
  const it = (s) => `<tspan font-style="italic">${s}</tspan>`;
  const m = (s, n = '') => it(s) + (n ? sub(n) : '');
  const sbar = '<tspan font-style="italic" text-decoration="overline">s</tspan>';
  const warm = '#8C725B';
  const trainingFill = '#FCFAF7';
  const fill = '#F8FAFB';

  d.rect('g-panel', 15, 307, 1418, 418, c.gf, c.g);
  d.text(25, 341, '(b) GCDL localization (G)', {size: 31, bold: true, fill: '#35516A'});
  d.rect('g1-frame', 30, 354, 640, 197, '#FCFDFE', '#7D99AF');
  d.rect('g2-frame', 681, 354, 738, 197, '#FCFDFE', '#7D99AF');
  d.text(41, 393, 'G.1 Distribution accumulation', {size: 25, bold: true, fill: '#35516A'});
  d.text(1407, 389, 'G.2 Center-preserving geometry', {size: 25, bold: true, fill: '#35516A', anchor: 'end'});
  d.rect('g3-frame', 30, 565, 1388, 140, trainingFill, warm, 0, {'stroke-dasharray': '5 3'});
  d.text(41, 599, 'G.3 LQS-weighted FGL • training only', {size: 25, bold: true, fill: '#715744'});

  // G.1: accumulated edge distributions. Only the query-feature skip is detached.
  d.node('g-query', 42, 414, 119, 55, ['Query features', m('h', 'l')], {fill, stroke: c.ink, fontSize: 19, rx: 3});
  d.node('g-prev-query', 42, 490, 110, 40, `sg(${m('h', 'l−1')})`, {fill, stroke: c.ink, fontSize: 21, rx: 3});
  d.node('g-query-add', 178, 441, 31, 31, '+', {fill: '#F9FAFC', stroke: c.ink, fontSize: 27, shape: 'circle'});
  d.node('g-edge-head', 222, 430, 101, 52, 'Edge head', {fill, stroke: c.ink, fontSize: 21, rx: 3});
  d.node('g-logit-add', 363, 441, 31, 31, '+', {fill: '#F9FAFC', stroke: c.ink, fontSize: 27, shape: 'circle'});
  d.node('g-integral', 417, 430, 157, 52, 'Softmax + Integral', {fill, stroke: c.ink, fontSize: 21, rx: 3});
  d.text(340, 443, m('Δz', 'l'), {size: 23, anchor: 'middle'});
  d.text(350, 512, m('z', 'l−1'), {size: 22, anchor: 'middle'});
  d.text(503, 523, `${m('z', 'l')} = ${m('z', 'l−1')} + ${m('Δz', 'l')}`, {size: 25, anchor: 'middle'});
  d.text(632, 446, 'offsets', {size: 22, anchor: 'middle'});
  d.edge('g-query-to-add', [[161, 445], [177, 445], [184, 447]], {source: 'g-query', target: 'g-query-add'});
  d.edge('g-prev-query-to-add', [[152, 510], [193.5, 510], [193.5, 472]], {source: 'g-prev-query', target: 'g-query-add'});
  d.edge('g-add-to-head', [[209, 456.5], [222, 456.5]], {source: 'g-query-add', target: 'g-edge-head'});
  d.edge('g-head-to-add', [[323, 456.5], [363, 456.5]], {source: 'g-edge-head', target: 'g-logit-add'});
  d.edge('g-prev-logits', [[378.5, 507], [378.5, 472]], {target: 'g-logit-add'});
  d.edge('g-add-to-integral', [[394, 456.5], [417, 456.5]], {source: 'g-logit-add', target: 'g-integral'});

  // G.2: one fixed decoding reference across layers; updated boxes serve attention.
  d.node('g-reference-fixed', 817, 323, 452, 28, `Fixed decoding reference ${m('r', '0')} (all six layers)`, {fill: '#F2F6F9', stroke: '#3E5265', fontSize: 19, textDy: -3, rx: 3});
  d.node('g-reference-offsets', 706, 425, 117, 61, ['Reference', '+ offsets'], {fill, stroke: c.ink, fontSize: 21, rx: 3});
  d.node('g-center', 863, 410, 113, 35, 'Center', {fill, stroke: c.ink, fontSize: 21, rx: 3});
  d.node('g-raw-extent', 863, 463, 113, 37, 'Raw extent', {fill, stroke: c.ink, fontSize: 21, rx: 3});
  d.node('g-extent-floor', 1004, 463, 109, 37, 'Extent floor', {fill: '#F4F0E9', stroke: c.ink, fontSize: 20, rx: 3});
  d.node('g-box-assembly', 1137, 420, 116, 61, ['Box', 'assembly'], {fill, stroke: c.ink, fontSize: 23, rx: 3});
  d.text(1058, 421, 'center unchanged', {size: 18, anchor: 'middle'});
  d.text(1060, 525, 'Positive extent', {size: 20, anchor: 'middle'});
  d.text(1275, 448, m('b', 'l'), {size: 25, anchor: 'middle'});
  d.text(1355, 452, [`sg(${m('b', 'l')}):`, 'next-layer', 'attention reference'], {size: 20, anchor: 'middle', lineHeight: 21, textWidth: 128});
  d.edge('g-integral-to-geometry', [[574, 456], [706, 456]], {source: 'g-integral', target: 'g-reference-offsets'});
  d.edge('g-fixed-reference-to-geometry', [[817, 337], [764.5, 337], [764.5, 425]], {source: 'g-reference-fixed', target: 'g-reference-offsets'});
  d.edge('g-offsets-to-center', [[823, 456], [836, 456], [836, 427.5], [863, 427.5]], {source: 'g-reference-offsets', target: 'g-center'});
  d.edge('g-offsets-to-extent', [[823, 456], [836, 456], [836, 481.5], [863, 481.5]], {source: 'g-reference-offsets', target: 'g-raw-extent'});
  d.edge('g-center-to-assembly', [[976, 427.5], [1137, 427.5]], {source: 'g-center', target: 'g-box-assembly'});
  d.edge('g-extent-to-floor', [[976, 481.5], [1004, 481.5]], {source: 'g-raw-extent', target: 'g-extent-floor'});
  d.edge('g-floor-to-assembly', [[1113, 481.5], [1128, 481.5], [1128, 465], [1137, 465]], {source: 'g-extent-floor', target: 'g-box-assembly'});
  d.edge('g-box-to-attention-reference', [[1253, 452], [1306, 452]], {source: 'g-box-assembly'});

  // G.3: detached matched-IoU quality is smoothed over eligible matches.
  d.node('g-matched-iou', 49, 643, 190, 41, `sg(matched IoU): ${m('s', 'i')}`, {fill: '#FCFAF7', stroke: warm, fontSize: 21, rx: 3});
  d.node('g-lqs', 277, 643, 145, 41, 'LQS smoothing', {fill: '#FCFAF7', stroke: warm, fontSize: 21, rx: 3});
  d.node('g-eligible-mean', 522, 581, 176, 47, [`Eligible mean ${sbar}`, '(over eligible samples)'], {fill: '#FCFAF7', stroke: warm, fontSize: 19, rx: 3});
  d.node('g-smoothed-quality', 477, 643, 265, 41, `${m('s′', 'i')} = (1 − ${m('α', 'l')}) ${m('s', 'i')} + ${m('α', 'l')}${sbar}`, {fill: '#FCFAF7', stroke: warm, fontSize: 24, rx: 3});
  d.node('g-fgl-weights', 776, 643, 149, 41, 'FGL weights', {fill: '#FCFAF7', stroke: warm, fontSize: 21, rx: 3});
  d.node('g-training-edge-logits', 969, 581, 160, 33, `edge logits ${m('z', 'l')}`, {fill: '#FCFAF7', stroke: warm, fontSize: 21, rx: 3});
  d.node('g-training-gt', 1166, 581, 207, 33, `GT encoded using ${m('r', '0')}`, {fill: '#FCFAF7', stroke: warm, fontSize: 20, rx: 3});
  d.node('g-fgl-loss', 966, 640, 178, 50, 'FGL loss', {fill: '#F1ECE5', stroke: warm, fontSize: 24, shape: 'ellipse'});
  const tr = {stroke: warm, dash: true};
  d.edge('g-iou-to-lqs', [[239, 665], [277, 665]], {...tr, source: 'g-matched-iou', target: 'g-lqs'});
  d.edge('g-lqs-to-quality', [[422, 665], [477, 665]], {...tr, source: 'g-lqs', target: 'g-smoothed-quality'});
  d.edge('g-mean-to-quality', [[610, 628], [610, 643]], {...tr, source: 'g-eligible-mean', target: 'g-smoothed-quality'});
  d.edge('g-quality-to-weights', [[742, 665], [776, 665]], {...tr, source: 'g-smoothed-quality', target: 'g-fgl-weights'});
  d.edge('g-weights-to-loss', [[925, 665], [966, 665]], {...tr, source: 'g-fgl-weights', target: 'g-fgl-loss'});
  d.edge('g-logits-to-fgl', [[1050, 614], [1050, 640]], {...tr, source: 'g-training-edge-logits', target: 'g-fgl-loss'});
  d.edge('g-gt-to-fgl', [[1203, 614], [1203, 665], [1144, 665]], {...tr, source: 'g-training-gt', target: 'g-fgl-loss'});
}
