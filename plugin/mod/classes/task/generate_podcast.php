<?php
namespace mod_owl\task;

defined('MOODLE_INTERNAL') || die();

class generate_podcast extends \core\task\adhoc_task {

    public function execute() {
        global $DB, $CFG;

        require_once($CFG->dirroot . '/mod/owl/locallib.php');

        $data       = $this->get_custom_data();
        $instanceid = (int) $data->instanceid;

        mtrace("owl generate_podcast: démarrage pour instance={$instanceid}");

        $record = $DB->get_record('owl', ['id' => $instanceid], 'id, extracted_text', MUST_EXIST);

        if (empty($record->extracted_text)) {
            mtrace("owl generate_podcast: aucun texte extrait disponible, abandon.");
            return;
        }

        $backendurl = owl_get_backend_url() . '/generate-podcast';

        $ch = curl_init($backendurl);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => http_build_query([
                'text'     => $record->extracted_text,
                'mode'     => 'duo',
                'provider' => 'openai',
            ]),
            CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
            CURLOPT_TIMEOUT        => 300,
        ]);

        $response = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curlerr  = curl_error($ch);
        curl_close($ch);

        if ($curlerr) {
            mtrace("owl generate_podcast: erreur curl: {$curlerr}");
            return;
        }

        if ($httpcode !== 200) {
            mtrace("owl generate_podcast: réponse HTTP {$httpcode}: {$response}");
            return;
        }

        $result = json_decode($response);
        if (!$result || empty($result->audio_url)) {
            mtrace("owl generate_podcast: réponse invalide ou audio_url manquant.");
            return;
        }

        $DB->set_field('owl', 'podcast_url', $result->audio_url, ['id' => $instanceid]);
        $DB->set_field('owl', 'status', 'podcast_ready', ['id' => $instanceid]);
        mtrace("owl generate_podcast: podcast généré, audio_url={$result->audio_url}");
    }
}
