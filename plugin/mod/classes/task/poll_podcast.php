<?php
namespace mod_owl\task;

defined('MOODLE_INTERNAL') || die();

class poll_podcast extends \core\task\adhoc_task {

    /** Maximum number of polling attempts before giving up. */
    const MAX_ATTEMPTS = 20;

    public function execute() {
        global $DB, $CFG;

        require_once($CFG->dirroot . '/mod/owl/locallib.php');

        $data       = $this->get_custom_data();
        $instanceid = (int) $data->instanceid;
        $jobid      = $data->job_id;
        $attempt    = isset($data->attempt) ? (int) $data->attempt : 1;

        $maxattempts = self::MAX_ATTEMPTS;
        mtrace("owl poll_podcast: tentative {$attempt}/{$maxattempts} pour instance={$instanceid}, job_id={$jobid}");

        if ($attempt > self::MAX_ATTEMPTS) {
            mtrace("owl poll_podcast: nombre maximum de tentatives atteint, abandon.");
            $DB->set_field('owl', 'status', 'podcast_failed', ['id' => $instanceid]);
            return;
        }

        $statusurl = owl_get_backend_url() . '/podcast/job/' . urlencode($jobid);

        $ch = curl_init($statusurl);
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPGET        => true,
            CURLOPT_TIMEOUT        => 15,
        ]);

        $response = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $curlerr  = curl_error($ch);
        curl_close($ch);

        if ($curlerr) {
            mtrace("owl poll_podcast: erreur curl: {$curlerr}");
            $this->requeue($instanceid, $jobid, $attempt);
            return;
        }

        if ($httpcode === 404) {
            mtrace("owl poll_podcast: job_id={$jobid} introuvable sur le backend, abandon.");
            $DB->set_field('owl', 'status', 'podcast_failed', ['id' => $instanceid]);
            return;
        }

        if ($httpcode !== 200) {
            mtrace("owl poll_podcast: réponse HTTP {$httpcode}: {$response}");
            $this->requeue($instanceid, $jobid, $attempt);
            return;
        }

        $result = json_decode($response);
        if (!$result || empty($result->status)) {
            mtrace("owl poll_podcast: réponse invalide.");
            $this->requeue($instanceid, $jobid, $attempt);
            return;
        }

        switch ($result->status) {
            case 'completed':
                if (empty($result->result->audio_url)) {
                    mtrace("owl poll_podcast: statut completed mais audio_url absent, abandon.");
                    $DB->set_field('owl', 'status', 'podcast_failed', ['id' => $instanceid]);
                    return;
                }
                $DB->set_field('owl', 'podcast_url', $result->result->audio_url, ['id' => $instanceid]);
                $DB->set_field('owl', 'status', 'podcast_ready', ['id' => $instanceid]);
                mtrace("owl poll_podcast: podcast prêt, audio_url={$result->result->audio_url}");
                break;

            case 'failed':
                $error = $result->error ?? 'inconnu';
                mtrace("owl poll_podcast: génération échouée sur le backend: {$error}");
                $DB->set_field('owl', 'status', 'podcast_failed', ['id' => $instanceid]);
                break;

            case 'pending':
            case 'processing':
                mtrace("owl poll_podcast: statut={$result->status}, nouvelle tentative dans 30s.");
                $this->requeue($instanceid, $jobid, $attempt);
                break;

            default:
                mtrace("owl poll_podcast: statut inconnu: {$result->status}, nouvelle tentative.");
                $this->requeue($instanceid, $jobid, $attempt);
        }
    }

    private function requeue(int $instanceid, string $jobid, int $attempt): void {
        $task = new self();
        $task->set_custom_data([
            'instanceid' => $instanceid,
            'job_id'     => $jobid,
            'attempt'    => $attempt + 1,
        ]);
        $task->set_next_run_time(time() + 30);
        \core\task\manager::queue_adhoc_task($task);
    }
}
