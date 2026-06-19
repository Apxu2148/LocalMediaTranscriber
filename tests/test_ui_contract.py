import re
import unittest
from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


class UiContractTests(unittest.TestCase):
    def test_unified_transcription_block_and_custom_file_pickers_exist(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        for element_id in (
            "queueSection",
            "transcriptionSources",
            "globalQueuePanel",
            "transcribeMicRecordingButton",
            "transcribeSystemRecordingButton",
            "transcribeAllRecordingsButton",
            "audioFilePickerButton",
            "audioFilePickerText",
            "refreshMicDevicesButton",
            "refreshOutputDevicesButton",
            "screenSourceCheckbox",
            "mouseSourceCheckbox",
            "keyboardSourceCheckbox",
            "inputSourceHint",
            "screenControls",
            "displayList",
            "screenFpsSelect",
            "whisperModelManager",
            "modelManagementSection",
            "modelManagerTable",
            "modelManagerBody",
            "modelDownloadProgress",
            "modelInfoPanel",
            "refreshModelsButton",
            "videoMuxForm",
            "videoMuxVideoSelect",
            "videoMuxMicSelect",
            "videoMuxSystemSelect",
            "videoMuxButton",
            "videoMuxOutput",
            "queueFilePickerButton",
            "queueFilePickerText",
            "queueStartButton",
            "queueClearButton",
            "defaultProcessingSettings",
            "defaultAudioEnabled",
            "defaultFramesEnabled",
            "defaultFrameRateSelect",
            "defaultJpegQualitySelect",
            "queueStageStatus",
            "queueMetrics",
            "queueProgress",
            "storagePanel",
            "storageSummaryGrid",
            "refreshStorageSummaryButton",
            "openDataFolderButton",
            "keepDownloadedMediaCheckbox",
            "keepUploadedTempCheckbox",
            "clearDownloadsButton",
            "clearUploadsButton",
            "storageCleanupOutput",
            "latestResultHeading",
            "transcriptText",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertGreaterEqual(html.count('class="native-file-input"'), 3)
        self.assertNotIn("operation-overlay", html)

    def test_ui_uses_queue_endpoints_instead_of_direct_transcription(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        self.assertIn('"/api/queue/add-recordings"', app_js)
        self.assertIn('"/api/queue/add-files"', app_js)
        self.assertIn('"/api/queue/add-urls"', app_js)
        self.assertIn('"/api/queue/start"', app_js)
        self.assertIn('"/api/queue/update-item"', app_js)
        self.assertIn('"/api/queue/remove-item"', app_js)
        self.assertIn('"/api/queue/cancel-item"', app_js)
        self.assertIn('"/api/queue/estimate-item"', app_js)
        self.assertIn('"/api/storage/summary"', app_js)
        self.assertIn('"/api/storage/settings"', app_js)
        self.assertIn('"/api/storage/cleanup"', app_js)
        self.assertIn('"/api/video-mux/merge"', app_js)
        self.assertIn('"/api/displays"', app_js)
        self.assertIn('"/api/displays/preview"', app_js)
        self.assertIn('"screen_fps"', app_js)
        self.assertIn('"display_indices"', app_js)
        self.assertIn('"record_mouse"', app_js)
        self.assertIn('"record_keyboard"', app_js)
        self.assertIn("syncInputSourceControls", app_js)
        self.assertIn("keyboardPrivacyHint", app_js)
        self.assertIn("sortDisplaysForLayout", app_js)
        self.assertIn("createDisplayCard", app_js)
        self.assertIn('input.name = "screenDisplay"', app_js)
        self.assertIn('previewCheckbox.name = "displayPreview"', app_js)
        self.assertIn('refreshButton.dataset.previewDisplay', app_js)
        self.assertIn("latestTechnicalItem.technical_details", app_js)
        self.assertIn("/api/transcripts/read", app_js)
        self.assertIn("loadTranscript(file.name, true)", app_js)
        self.assertIn('transcriptText.value = result.text || "";', app_js)
        self.assertIn("frameRateOptions", app_js)
        self.assertIn("data-queue-operation", app_js)
        self.assertIn("data-queue-frame-rate", app_js)
        self.assertIn("data-queue-jpeg-quality", app_js)
        self.assertIn("75, 80, 85, 90, 95, 100", app_js)
        self.assertIn('t("downloadedMediaResultPath"', app_js)
        self.assertIn('t("transcriptResultPath"', app_js)
        self.assertIn('t("framesResultFolder"', app_js)
        self.assertIn('t("framesResultCount"', app_js)
        self.assertIn('t("framesResultIndex"', app_js)
        self.assertIn('t("frameEstimateAfterDownload"', app_js)
        self.assertIn('t("selectAtLeastOneUrlOperation"', app_js)
        self.assertIn('queueItem.source_type === "url"', app_js)
        self.assertIn("queueItemOutputLines", app_js)
        self.assertIn("queueItemArtifactLines", app_js)
        self.assertIn("outputArtifactsTitle", app_js)
        self.assertIn("downloaded_media_deleted", app_js)
        self.assertIn("uploaded_temp_deleted", app_js)
        self.assertIn("cleanupStorageFolder", app_js)
        self.assertIn("refreshStorageSummary", app_js)
        self.assertIn("function setLocalizedOutput", app_js)
        self.assertIn('setLocalizedOutput(storageCleanupOutput, "storageSettingsSaved", {}, "success")', app_js)
        self.assertNotIn('"Storage settings saved."', app_js)
        self.assertNotIn('"Настройки хранения сохранены."', app_js)
        self.assertIn("displayOutputPath", app_js)
        self.assertIn('lastIndexOf("/data/")', app_js)
        self.assertIn("queueStageLabel", app_js)
        self.assertIn("updateQueueStageStatus", app_js)
        self.assertIn("queue-item-stage", app_js)
        self.assertIn("isAddingFile", app_js)
        self.assertIn("isAddingUrl", app_js)
        self.assertIn("pendingAddKeys", app_js)
        self.assertIn("showAddStatus", app_js)
        self.assertIn("frameCountWarning", app_js)
        self.assertIn("removeFromQueue", app_js)
        self.assertIn("cancelCurrentItem", app_js)
        self.assertIn("cancelCurrentShort", app_js)
        self.assertIn("cancelTranscription", app_js)
        self.assertIn("transcriptionCancelAfterSegment", app_js)
        self.assertIn("runningItemCannotCancel", app_js)
        self.assertIn("cancelling_transcription", app_js)
        self.assertIn("partialTranscriptArtifactPath", app_js)
        self.assertIn("formatQueueItemError", app_js)
        self.assertIn("frameWriteError", app_js)
        self.assertIn("queueControlHasActiveFocus", app_js)
        self.assertIn("preserveFocusedQueueControls", app_js)
        self.assertIn('"/api/models/download"', app_js)
        self.assertIn('"/api/models/download-status"', app_js)
        self.assertIn('"/api/models/verify"', app_js)
        self.assertIn('"/api/models/delete"', app_js)
        self.assertIn("/api/models/info", app_js)
        self.assertIn("latestMicDevicesResult = inputResult", app_js)
        self.assertIn("latestOutputDevicesResult = outputResult", app_js)
        self.assertIn("fillMicDevices(latestMicDevicesResult, micDeviceSelect.value)", app_js)
        self.assertIn("fillOutputDevices(latestOutputDevicesResult, outputDeviceSelect.value)", app_js)
        self.assertIn("function recordingUsesMicInput()", app_js)
        self.assertIn("function recordingUsesSystemAudio()", app_js)
        self.assertIn("if (!recordingUsesMicInput())", app_js)
        self.assertIn('resetLevel(micLevelTarget(), t("micLevelInactive"), "info")', app_js)
        self.assertIn("if (!recordingUsesSystemAudio())", app_js)
        self.assertIn('resetLevel(systemLevelTarget(), t("systemLevelInactive"), "info")', app_js)
        self.assertNotIn("navigator.mediaDevices.getUserMedia", app_js)
        self.assertNotIn("AudioContext", app_js)
        self.assertIn('t("defaultSuffix")', app_js)
        self.assertNotIn('"/api/transcribe"', app_js)
        self.assertNotIn('"/api/transcribe/file"', app_js)

    def test_model_status_copy_is_localized_and_progress_can_clear(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertIsNone(re.search(r"[А-Яа-яЁё]", app_js))
        self.assertIsNone(re.search(r"[А-Яа-яЁё]", html))
        for key in (
            "modelStatusReady",
            "modelStatusDownloading",
            "modelStatusVerifying",
            "modelStatusFailed",
            "modelProgressPercent",
            "modelProgressUnavailable",
            "modelDownloadInProgress",
            "modelDownloadCompleted",
            "modelVerifySuccess",
            "modelVerifyFailed",
        ):
            self.assertIn(f't("{key}"', app_js)

        self.assertIn("function clearModelDownloadProgressUi()", app_js)
        self.assertIn("function clearModelDownloadProgressForModel(model)", app_js)
        self.assertIn('modelDownloadProgress.removeAttribute("value")', app_js)
        self.assertNotIn("Downloading model", app_js)
        self.assertNotIn("Progress:", app_js)

    def test_default_processing_settings_and_plan_contract_exist(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertEqual(1, html.count('id="whisperModelSelect"'))
        self.assertEqual(1, html.count('id="whisperDeviceSelect"'))
        self.assertLess(html.index('id="queueRetryButton"'), html.index('id="defaultProcessingSettings"'))
        for element_id in (
            "defaultProcessingSettings",
            "defaultAudioEnabled",
            "defaultFramesEnabled",
            "defaultFrameRateSelect",
            "defaultJpegQualitySelect",
        ):
            self.assertIn(f'id="{element_id}"', html)
        for key in (
            "defaultProcessingSettingsTitle",
            "appliesToNewQueueItems",
            "itemSettingsOverrideDefaults",
            "processingPlan",
            "processingPlanAudio",
            "processingPlanFrames",
            "processingPlanOcr",
            "processingPlanCv",
            "disabled",
            "comingSoon",
            "computerVision",
            "ocrEngineComingSoon",
            "cvEngineComingSoon",
        ):
            self.assertIn(key, html + app_js)
        self.assertIn("defaultProcessingPlanSnapshot", app_js)
        self.assertIn("processingPlanForQueueItem", app_js)
        self.assertIn("processing_plan", app_js)
        self.assertIn('status: "coming_soon"', app_js)
        self.assertIn('disabled>', html)
        self.assertNotIn("Tesseract OCR (coming soon)", app_js)
        self.assertNotIn("Basic OpenCV (coming soon)", app_js)

    def test_runtime_estimate_action_and_result_contract_exist(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")

        self.assertIsNone(re.search(r"[А-Яа-яЁё]", app_js))
        self.assertIsNone(re.search(r"[А-Яа-яЁё]", html))
        self.assertIn('button.dataset.queueAction = "estimate"', app_js)
        self.assertIn('wrapper.dataset.runtimeEstimateResult = "true"', app_js)
        self.assertIn("function createRuntimeEstimate(queueItem, status)", app_js)
        self.assertIn("function formatReadableEstimateDuration(seconds)", app_js)
        self.assertIn("function runRuntimeEstimate(card)", app_js)
        self.assertIn("pendingRuntimeEstimateIds", app_js)
        self.assertIn("runtimeEstimateActive", app_js)
        self.assertIn("estimateDetails", app_js)
        self.assertIn("noEnabledOperationsEstimate", app_js)
        self.assertIn("createComingSoonOption(\"ocr\")", app_js)
        self.assertIn("createComingSoonOption(\"cv\")", app_js)
        self.assertIn(".queue-runtime-estimate", css)
        self.assertIn(".queue-estimate-button", css)

    def test_processing_plan_polish_contract(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('id="transcriptionSettings"', html)
        self.assertNotIn('data-i18n="settingsTitle"', html)
        self.assertNotIn('data-i18n="settingsNote"', html)
        self.assertNotIn("Настройки транскрибации", html)
        self.assertIn("function modelOptionLabel(model)", app_js)
        self.assertIn("function populateModelSelect(select, selectedValue)", app_js)
        self.assertIn("populateModelSelect(whisperModelSelect, selectedModel())", app_js)
        self.assertIn('modelOptionLabel,', app_js)
        self.assertIn("audioRuntimeStages", app_js)
        self.assertIn("processingPlanForQueueItem(current).audio", app_js)
        self.assertIn('t("statusNotApplicable")', app_js)
        self.assertEqual(1, app_js.count("runtimeModel.textContent ="))
        self.assertEqual(1, app_js.count("runtimeDevice.textContent ="))
        self.assertEqual(1, app_js.count("runtimeCompute.textContent ="))
        self.assertEqual(1, app_js.count("runtimeSpeed.textContent ="))
        self.assertIn("pendingQueueCancellationIds", app_js)
        self.assertIn("queueItem.cancel_requested", app_js)
        self.assertIn('button.textContent = t("cancelling")', app_js)
        self.assertIn('t("cancelRequestSent")', app_js)

    def test_queue_start_button_uses_processing_copy(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")

        self.assertIn('id="queueStartButton" type="button" data-i18n="startProcessing"', html)
        self.assertIn('startProcessing: "Start processing"', i18n)
        self.assertNotIn('data-i18n="startTranscription"', html)
        self.assertNotIn('Start transcription"', i18n)

    def test_video_frame_queue_controls_and_avi_accept_contract_exist(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
        self.assertGreaterEqual(html.count(".avi"), 3)
        self.assertIn("video/x-msvideo", html)
        self.assertIn("isQueueVideoFile", app_js)
        self.assertIn('".avi"', app_js)
        self.assertIn('".mov"', app_js)
        self.assertIn(".mov", html)
        self.assertIn("video/quicktime", html)
        self.assertIn("queue-item-remove", app_js)
        self.assertIn("queue-item-cancel", app_js)
        self.assertIn("queue-stage-status", css)
        self.assertIn(".queue-item-stage", css)
        self.assertIn("queue-frame-settings", app_js)
        self.assertIn("queue-frame-result", app_js)
        self.assertIn(".queue-item-card", css)
        self.assertIn(".queue-frame-settings", css)

    def test_file_benchmark_order_and_recording_help_location(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        self.assertLess(html.index('id="whisperModelManager"'), html.index('id="recordingSection"'))
        self.assertLess(html.index('id="recordingSection"'), html.index('id="queueSection"'))
        self.assertLess(html.index('id="recordingTranscribeActions"'), html.index('id="videoMuxForm"'))
        self.assertLess(html.index('id="videoMuxForm"'), html.index('id="transcribeForm"'))
        self.assertLess(html.index('id="transcribeForm"'), html.index('id="benchmarkSection"'))
        self.assertLess(html.index('id="queueSection"'), html.index('id="benchmarkSection"'))
        self.assertLess(html.index('id="filesSection"'), html.index('id="benchmarkSection"'))
        self.assertLess(html.index('class="recording-device-grid"'), html.index('id="helpSection"'))
        self.assertLess(html.index('id="helpSection"'), html.index('id="queueSection"'))
        self.assertIn('data-i18n="helpDeviceSummary"', html)

    def test_display_cards_and_preview_contract_exist(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
        self.assertIn('data-i18n="selectDisplaysToRecord"', html)
        self.assertIn("display-card", app_js)
        self.assertIn("display-preview-controls", app_js)
        self.assertIn("display-preview-frame", app_js)
        self.assertIn(".display-card", css)
        self.assertIn(".display-preview-frame", css)

    def test_recordings_and_transcripts_lists_are_compact(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
        self.assertIn('data-i18n="recentRecordings"', html)
        self.assertIn('id="recordingsFileList" class="file-list compact-file-list"', html)
        self.assertIn('id="transcriptsFileList" class="file-list compact-file-list"', html)
        self.assertIn(".compact-file-list", css)
        self.assertIn("max-height: 300px;", css)
        self.assertIn("overflow-y: auto;", css)

    def test_files_and_benchmark_sections_are_collapsible_by_default(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")
        self.assertIn('<details id="filesSection" class="workspace-section collapsible-section">', html)
        self.assertIn('<details id="benchmarkSection" class="workspace-section collapsible-section">', html)
        self.assertIn('data-i18n="show"', html)
        self.assertIn('data-i18n="hide"', html)
        self.assertIn(".collapsible-section[open]", css)

    def test_favicon_link_exists(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        icon = STATIC_DIR / "icons" / "favicon.svg"
        self.assertIn('href="/static/icons/favicon.svg"', html)
        self.assertTrue(icon.exists())

    def test_tour_targets_current_html_elements(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        tour_js = (STATIC_DIR / "tour.js").read_text(encoding="utf-8")
        selectors = re.findall(r'\["(#[A-Za-z][A-Za-z0-9_-]*)",\s*"tour', tour_js)
        self.assertGreaterEqual(len(selectors), 10)
        for selector in selectors:
            self.assertIn(f'id="{selector[1:]}"', html, selector)

    def test_tour_buttons_are_back_next_finish_order(self) -> None:
        tour_js = (STATIC_DIR / "tour.js").read_text(encoding="utf-8")
        self.assertLess(tour_js.index('createButton("tourBack"'), tour_js.index('createButton("tourNext"'))
        self.assertLess(tour_js.index('createButton("tourNext"'), tour_js.index('createButton("tourFinish"'))
        self.assertIn('actions.children[0].dataset.role = "back"', tour_js)
        self.assertIn('actions.children[1].dataset.role = "next"', tour_js)
        self.assertIn('actions.children[2].dataset.role = "finish"', tour_js)


if __name__ == "__main__":
    unittest.main()
