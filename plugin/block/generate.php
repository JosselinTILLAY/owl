<?php
require_once(__DIR__ . '/../../config.php');
require_once(__DIR__ . '/generate_form.php');

$courseid = required_param('courseid', PARAM_INT);

$course  = $DB->get_record('course', ['id' => $courseid], '*', MUST_EXIST);
$context = context_course::instance($courseid);

require_login($course);
require_capability('moodle/course:manageactivities', $context);

$PAGE->set_url('/blocks/owl/generate.php', ['courseid' => $courseid]);
$PAGE->set_context($context);
$PAGE->set_title(get_string('pluginname', 'block_owl'));
$PAGE->set_heading($course->fullname);
$PAGE->set_pagelayout('incourse');

// Topics du cours (sections avec nom)
$rawsections = $DB->get_records('course_sections', ['course' => $courseid], 'section ASC', 'id, section, name, summary');
$sections = [];
foreach ($rawsections as $sec) {
    $label = $sec->name ?: get_string('section') . ' ' . $sec->section;
    $sections[$sec->id] = $label;
}

// Ressources existantes du cours (activités de type contenu)
$allowed_modtypes = ['resource', 'page', 'label', 'url', 'folder'];
$modinfo = get_fast_modinfo($course);
$course_resources = [];
foreach ($modinfo->cms as $cm) {
    if (in_array($cm->modname, $allowed_modtypes) && $cm->uservisible) {
        $course_resources[$cm->id] = '[' . $cm->modname . '] ' . $cm->name;
    }
}

// Draft area pour le filemanager
$draftitemid = file_get_submitted_draft_itemid('documents');
file_prepare_draft_area($draftitemid, $context->id, 'block_owl', 'documents', 0);

$form = new block_owl_generate_form(null, ['sections' => $sections, 'course_resources' => $course_resources]);
$form->set_data(['courseid' => $courseid, 'documents' => $draftitemid]);

$returnurl = new moodle_url('/course/view.php', ['id' => $courseid]);

if ($form->is_cancelled()) {
    redirect($returnurl);
}

if ($data = $form->get_data()) {
    // Sauvegarde les fichiers depuis la draft area
    file_save_draft_area_files(
        $data->documents,
        $context->id,
        'block_owl',
        'documents',
        0
    );

    // TODO: déclencher la génération via le provider configuré ($data->type)
    // $data->sectionid : section cible dans le cours
    // $data->prompt    : instructions supplémentaires de l'utilisateur

    redirect(new moodle_url('/blocks/owl/pending.php', ['courseid' => $courseid]));
}

echo $OUTPUT->header();
echo $OUTPUT->heading(get_string('pluginname', 'block_owl'));
$form->display();
echo $OUTPUT->footer();
