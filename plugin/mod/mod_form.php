<?php
defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/course/moodleform_mod.php');

class mod_owl_mod_form extends moodleform_mod {

    public function definition() {
        global $COURSE, $PAGE;
        $mform = $this->_form;

        // Type de génération — placé AVANT le nom pour que le JS puisse l'écouter
        $types = [
            'podcast' => get_string('type_podcast', 'mod_owl'),
            'video'   => get_string('type_video',   'mod_owl'),
            'qcm'     => get_string('type_qcm',     'mod_owl'),
        ];
        $mform->addElement('select', 'type', get_string('form_type', 'mod_owl'), $types);
        $mform->setDefault('type', 'podcast');

        // En-tête général + Nom (sans required — fallback dans owl_add_instance)
        $mform->addElement('header', 'general', get_string('general', 'form'));
        $mform->addElement('text', 'name', get_string('name'), ['size' => '64']);
        $mform->addRule('name', get_string('maximumchars', '', 255), 'maxlength', 255, 'client');
        $mform->setType('name', PARAM_TEXT);

        // Description (intro)
        $mform->addElement('editor', 'introeditor', get_string('moduleintro'), null, ['maxfiles' => EDITOR_UNLIMITED_FILES, 'noclean' => true, 'context' => $this->context, 'subdirs' => true]);
        $mform->setType('introeditor', PARAM_RAW);

        // JS : auto-remplit le nom selon le type si le prof ne l'a pas saisi manuellement
        $typelabels = json_encode([
            'podcast' => get_string('type_podcast', 'mod_owl'),
            'video'   => get_string('type_video',   'mod_owl'),
            'qcm'     => get_string('type_qcm',     'mod_owl'),
        ]);
        $PAGE->requires->js_amd_inline("
            require(['jquery'], function(\$) {
                var labels   = $typelabels;
                var nameEl   = \$('#id_name');
                var typeEl   = \$('#id_type');
                var autoFill = nameEl.val() === '';

                nameEl.on('input', function() { autoFill = false; });

                typeEl.on('change', function() {
                    if (autoFill) { nameEl.val(labels[typeEl.val()] || ''); }
                });

                if (autoFill) { nameEl.val(labels[typeEl.val()] || ''); }
            });
        ");

        // Ressources existantes du cours
        $allowed_modtypes = ['resource', 'page', 'label', 'url', 'folder'];
        $modinfo = get_fast_modinfo($COURSE);
        $course_resources = [];
        foreach ($modinfo->cms as $cm) {
            if (in_array($cm->modname, $allowed_modtypes) && $cm->uservisible) {
                $course_resources[$cm->id] = '[' . $cm->modname . '] ' . $cm->name;
            }
        }
        if (!empty($course_resources)) {
            $mform->addElement(
                'autocomplete',
                'course_resources',
                get_string('form_course_resources', 'mod_owl'),
                $course_resources,
                ['multiple' => true, 'noselectionstring' => get_string('form_course_resources_none', 'mod_owl')]
            );
        }

        // Prompt
        $mform->addElement('textarea', 'prompt', get_string('form_prompt', 'mod_owl'), ['rows' => 4, 'cols' => 60]);
        $mform->setType('prompt', PARAM_TEXT);
        $mform->addHelpButton('prompt', 'form_prompt', 'mod_owl');

        // Upload de documents
        $options = [
            'subdirs'        => 0,
            'maxfiles'       => 20,
            'accepted_types' => ['.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx', '.odt', '.odp'],
        ];
        $mform->addElement('filemanager', 'documents', get_string('form_documents', 'mod_owl'), null, $options);

        // Éléments standard Moodle (visible, groupe, etc.)
        $this->standard_coursemodule_elements();
        $this->add_action_buttons();
    }

    public function data_preprocessing(&$defaultvalues) {
        parent::data_preprocessing($defaultvalues);

        // Prépare la draft area pour le filemanager en mode édition
        $draftitemid = file_get_submitted_draft_itemid('documents');
        if (!empty($this->current->instance)) {
            $context = context_module::instance($this->current->coursemodule);
            file_prepare_draft_area(
                $draftitemid,
                $context->id,
                'mod_owl',
                'documents',
                $this->current->instance,
                ['subdirs' => 0, 'maxfiles' => 20]
            );
        }
        $defaultvalues['documents'] = $draftitemid;
    }

    public function validation($data, $files) {
        $errors = parent::validation($data, $files);

        $hasresources = !empty($data['course_resources']);
        $hasdocs = !empty($data['documents']) && $data['documents'] != 0;

        if (!$hasresources && !$hasdocs) {
            $errors['documents'] = get_string('form_sources_required', 'mod_owl');
        }

        return $errors;
    }
}
