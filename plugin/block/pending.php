<?php
require_once(__DIR__ . '/../../config.php');

$courseid = required_param('courseid', PARAM_INT);

$course  = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
$context = context_course::instance($courseid);

require_login($course);
require_capability('moodle/course:manageactivities', $context);

$PAGE->set_url('/blocks/owl/pending.php', ['courseid' => $courseid]);
$PAGE->set_context($context);
$PAGE->set_title(get_string('pending_title', 'block_owl'));
$PAGE->set_heading($course->fullname);
$PAGE->set_pagelayout('incourse');

$courseurl = new moodle_url('/course/view.php', ['id' => $courseid]);

echo $OUTPUT->header();
echo $OUTPUT->heading(get_string('pending_heading', 'block_owl'));

echo html_writer::div(
    html_writer::tag('p', get_string('pending_message', 'block_owl')) .
    html_writer::tag('p', get_string('pending_hint', 'block_owl')),
    'alert alert-info'
);

echo html_writer::div(
    html_writer::link($courseurl, get_string('pending_back', 'block_owl'), ['class' => 'btn btn-primary']),
    'mt-3'
);

echo $OUTPUT->footer();
