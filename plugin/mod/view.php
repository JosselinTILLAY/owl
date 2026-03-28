<?php
require_once(__DIR__ . '/../../config.php');

$id = required_param('id', PARAM_INT); // course module id

$cm     = get_coursemodule_from_id('owl', $id, 0, false, MUST_EXIST);
$course = $DB->get_record('course', ['id' => $cm->course], '*', MUST_EXIST);
$owl    = $DB->get_record('owl', ['id' => $cm->instance], '*', MUST_EXIST);

require_login($course, true, $cm);
$context = context_module::instance($cm->id);

$PAGE->set_url('/mod/owl/view.php', ['id' => $cm->id]);
$PAGE->set_title(format_string($owl->name));
$PAGE->set_heading($course->fullname);
$PAGE->set_pagelayout('incourse');

echo $OUTPUT->header();
echo $OUTPUT->heading(format_string($owl->name));

if ($owl->status === 'podcast_ready' && !empty($owl->podcast_url)) {
    echo html_writer::tag('audio', '', [
        'controls'    => 'controls',
        'src'         => $owl->podcast_url,
        'style'       => 'width:100%;margin-top:1em;',
    ]);
} else if ($owl->status === 'podcast_failed') {
    echo html_writer::div(
        html_writer::tag('p', get_string('podcast_failed', 'mod_owl')),
        'alert alert-danger'
    );
} else {
    // pending / ready / generating : afficher le message d'attente et rafraîchir
    $message = in_array($owl->status, ['ready', 'generating'])
        ? get_string('generating_message', 'mod_owl') . html_writer::tag('p', get_string('generating_hint', 'mod_owl'))
        : get_string('pending_message', 'mod_owl') . html_writer::tag('p', get_string('pending_hint', 'mod_owl'));

    echo html_writer::div(html_writer::tag('p', $message), 'alert alert-info');

    $PAGE->requires->js_amd_inline("
        setTimeout(function() { window.location.reload(); }, 15000);
    ");
}

echo $OUTPUT->footer();
