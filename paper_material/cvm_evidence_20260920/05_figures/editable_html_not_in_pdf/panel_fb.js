function buildFB(d) {
  const c = d.c;
  const sub = value => `<tspan baseline-shift="sub" font-size="70%" font-style="${/[a-z]/i.test(value) ? 'italic' : 'normal'}">${value}</tspan>`;
  const sup = value => `<tspan baseline-shift="super" font-size="70%">${value}</tspan>`;
  const it = value => `<tspan font-style="italic">${value}</tspan>`;
  const p3 = `${it('P')}${sub('3')}`;
  const p3s = `${it('P')}${sub('3')}${sup('*')}`;
  const r0 = `${it('r')}${sub('0')}`;

  // Panel (c): shared P3 refinement.
  d.rect('f_frame', 15, 745, 602, 274, '#FFFFFF', c.f);
  d.rect('f_header', 15, 745, 602, 41, c.ff, c.f);
  d.text(25, 776, `(c) Shared P${sub('3')} refinement (F)`, {
    size: 28, fill: c.f, bold: true, id: 'f_title', textWidth: 311
  });

  d.edge('f_input', [[30, 857], [83, 857]], {stroke: c.f, target: 'f_residual'});
  d.edge('f_to_gates', [[179, 857], [192, 857]], {source: 'f_residual', target: 'f_gates'});
  d.edge('f_to_blend', [[299, 857], [334, 857]], {stroke: c.f, source: 'f_gates', target: 'f_blend'});
  d.edge('f_skip', [[57, 857], [57, 957], [419, 957], [419, 909]], {stroke: c.f, target: 'f_blend'});
  d.edge('f_output', [[504, 858], [534, 858]], {stroke: c.f, source: 'f_blend'});

  d.node('f_residual', 83, 825, 96, 62, ['Residual', 'blocks × 2'], {
    fill: c.neutral, stroke: c.ink, fontSize: 19, lineHeight: 23
  });
  d.node('f_gates', 192, 825, 107, 62, ['Channel +', 'spatial gates'], {
    fill: c.neutral, stroke: c.ink, fontSize: 19, lineHeight: 23
  });
  d.node('f_blend', 334, 828, 170, 81, [
    'Residual blend',
    `${p3s} = ${p3} + ${it('γ')} (${it('R')} − ${p3})`
  ], {fill: c.neutral, stroke: c.ink, fontSize: 19, lineHeight: 31});
  d.text(30, 849, p3, {size: 20, fill: c.f, id: 'f_input_label'});
  d.text(309, 846, 'R', {size: 20, fill: c.f, id: 'f_refined_label'});
  d.text(540, 863, p3s, {size: 22, fill: c.f, id: 'f_output_label'});
  d.text(199, 948, `${p3} skip`, {size: 20, id: 'f_skip_label'});
  d.text(568, 919, ['Shared by', 'decoder and', 'local expert'], {
    size: 17, fill: c.f, anchor: 'middle', lineHeight: 18, id: 'f_shared_label'
  });

  // Panel (d): box-conditioned local expert.
  d.rect('b_frame', 635, 745, 798, 274, '#FFFFFF', c.b);
  d.rect('b_header', 635, 745, 798, 36, c.bf, c.b);
  d.text(646, 776, '(d) Box-conditioned local expert (B)', {
    size: 28, fill: c.b, bold: true, id: 'b_title', textWidth: 370
  });
  d.rect('b_training_frame', 646, 913, 776, 102, '#FFFFFF', c.b, 0, {'stroke-dasharray': '5 3'});

  d.edge('b_query_to_attention', [[813, 820], [848, 820], [848, 840], [865, 840]], {
    source: 'b_query', target: 'b_attention'
  });
  d.edge('b_tokens_to_attention', [[814, 881], [848, 881], [848, 867], [865, 867]], {
    source: 'b_tokens', target: 'b_attention'
  });
  d.edge('b_attention_to_ln', [[982, 852], [1004, 852]], {source: 'b_attention', target: 'b_ln'});
  d.edge('b_ln_to_class', [[1062, 852], [1079, 852], [1079, 820], [1102, 820]], {
    source: 'b_ln', target: 'b_class_residual'
  });
  d.edge('b_ln_to_edge', [[1062, 852], [1079, 852], [1079, 881], [1101, 881]], {
    source: 'b_ln', target: 'b_edge_residual'
  });
  d.edge('b_class_to_add', [[1218, 821], [1241, 821]], {source: 'b_class_residual', target: 'b_class_add'});
  d.edge('b_base_class', [[1255, 799], [1255, 807]], {target: 'b_class_add'});
  d.edge('b_class_to_output', [[1269, 821], [1353, 821]], {source: 'b_class_add', target: 'b_classes'});
  d.edge('b_edge_to_add', [[1209, 881], [1226, 881]], {source: 'b_edge_residual', target: 'b_edge_add'});
  d.edge('b_base_edge', [[1241, 857], [1241, 866]], {target: 'b_edge_add'});
  d.edge('b_add_to_decode', [[1256, 881], [1272, 881]], {source: 'b_edge_add', target: 'b_decode'});
  d.edge('b_decode_to_boxes', [[1354, 881], [1369, 881]], {source: 'b_decode', target: 'b_boxes'});

  d.node('b_query', 650, 794, 163, 51, ['Augmented query', `final query, sg(${it('μ')}, ${it('H')})`], {
    fill: c.neutral, stroke: c.ink, fontSize: 18, lineHeight: 20
  });
  d.node('b_tokens', 650, 855, 164, 50, ['Local tokens', `${it('P')}${sub('2')}, ${p3s}, ${it('P')}${sub('4')}; sg(base box)`], {
    fill: c.neutral, stroke: c.ink, fontSize: 18, lineHeight: 20
  });
  d.node('b_attention', 865, 823, 117, 58, ['Local attention', '+ FFN × 2'], {
    fill: c.neutral, stroke: c.ink, fontSize: 18, lineHeight: 21
  });
  d.node('b_ln', 1004, 828, 58, 51, ['Final', 'LN'], {
    fill: c.neutral, stroke: c.ink, fontSize: 19, lineHeight: 21
  });
  d.node('b_class_residual', 1102, 805, 116, 31, 'Class residual', {
    fill: c.bf, stroke: c.b, fontSize: 18
  });
  d.node('b_edge_residual', 1101, 866, 108, 31, 'Edge residual', {
    fill: c.bf, stroke: c.b, fontSize: 18
  });
  d.node('b_class_add', 1241, 807, 28, 28, '+', {fill: c.neutral, stroke: c.ink, fontSize: 25, shape: 'circle'});
  d.node('b_edge_add', 1226, 866, 30, 30, '+', {fill: c.neutral, stroke: c.ink, fontSize: 25, shape: 'circle'});
  d.node('b_classes', 1353, 807, 70, 30, 'Classes', {fill: c.neutral, stroke: c.ink, fontSize: 18});
  d.node('b_decode', 1272, 861, 82, 44, ['Decode', `with same ${r0}`], {
    fill: c.bf, stroke: c.ink, fontSize: 16, lineHeight: 18
  });
  d.node('b_boxes', 1369, 868, 54, 28, 'Boxes', {fill: c.neutral, stroke: c.ink, fontSize: 18});
  d.text(1263, 797, 'base class', {size: 17, anchor: 'middle', id: 'b_base_class_label'});
  d.text(1263, 855, 'base edge logits', {size: 17, anchor: 'middle', id: 'b_base_edge_label'});

  // The detached teacher receives the combined expert logits.
  d.edge('b_teacher_to_loss', [[904, 954], [1094, 954]], {
    stroke: c.b, dash: true, source: 'b_teacher_logits', target: 'b_kl_loss'
  });
  d.edge('b_student_to_loss', [[904, 996], [1094, 969]], {
    stroke: c.b, dash: true, source: 'b_student_logits', target: 'b_kl_loss'
  });
  d.node('b_teacher_logits', 676, 940, 228, 44, ['sg(base edge logits', '+ edge residual)'], {
    fill: c.bf, stroke: c.b, fontSize: 18, lineHeight: 20
  });
  d.node('b_student_logits', 690, 987, 214, 25, 'G edge logits', {fill: c.bf, stroke: c.b, fontSize: 19});
  d.node('b_kl_loss', 1094, 936, 207, 49, 'Masked KL loss', {
    fill: c.bf, stroke: c.b, fontSize: 22, shape: 'ellipse'
  });
  d.node('b_teacher_label', 916, 941, 62, 26, 'Teacher', {
    fill: '#FFFFFF', stroke: 'none', fontSize: 18, rx: 0
  });
  d.node('b_student_label', 916, 982, 66, 26, 'Student', {
    fill: '#FFFFFF', stroke: 'none', fontSize: 18, rx: 0
  });
  d.text(652, 935, 'Selective distillation · training only', {
    size: 20, fill: c.b, bold: true, id: 'b_training_title', textWidth: 245
  });
  d.text(1328, 971, 'Supervises G', {size: 17, id: 'b_supervision_label', textWidth: 82});
  d.text(1070, 1008, 'Shared assignment + quality / IoU checks', {
    size: 18, id: 'b_shared_checks', textWidth: 291
  });

  // Bottom legend.
  d.rect('legend_frame', 15, 1036, 1418, 39, '#FFFFFF', c.border, 1);
  d.edge('legend_forward_arrow', [[100, 1055], [147, 1055]], {stroke: c.ink});
  d.text(163, 1061, 'Forward computation', {size: 18, id: 'legend_forward_label', textWidth: 127});
  d.edge('legend_training_arrow', [[379, 1055], [425, 1055]], {stroke: c.b, dash: true});
  d.text(440, 1061, 'Training only', {size: 18, id: 'legend_training_label', textWidth: 81});
  d.text(667, 1061, 'sg:  stop-gradient', {size: 18, id: 'legend_stop_gradient', textWidth: 95});
  d.text(901, 1061, `${it('h')}${sub('l')}:  query features`, {size: 18, id: 'legend_query_features', textWidth: 109});
  d.text(1168, 1061, `${it('s')}${sub('i')}:  matched-IoU quality`, {size: 18, id: 'legend_iou_quality', textWidth: 145});
}
