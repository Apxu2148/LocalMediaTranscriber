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
            "queueFolderNameInput",
            "queueFolderPathOutput",
            "defaultProcessingSettings",
            "defaultAudioEnabled",
            "defaultFramesEnabled",
            "defaultFrameRateSelect",
            "defaultJpegQualitySelect",
            "defaultFrameMaxSizeSelect",
            "urlDownloadSettingsPanel",
            "urlDownloadProfileSelect",
            "urlDownloadMaxVideoHeightSelect",
            "urlDownloadCustomField",
            "urlDownloadCustomFormatInput",
            "urlDownloadLogMediaProbe",
            "urlDownloadLogExtractionBenchmark",
            "urlDownloadSaveButton",
            "urlDownloadSettingsOutput",
            "ocrSettingsPanel",
            "ocrStatusBadge",
            "ocrBackendType",
            "ocrVersion",
            "ocrLanguages",
            "ocrCheckButton",
            "ocrStatusMessage",
            "ocrBackendNotes",
            "defaultOcrEnabled",
            "defaultOcrTesseract",
            "defaultOcrPaddle",
            "defaultOcrWindows",
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
            "transcriptPreviewSection",
            "latestResultHeading",
            "transcriptPathForm",
            "transcriptPathInput",
            "transcriptPathLoadButton",
            "transcriptPreviewOutput",
            "transcriptText",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertGreaterEqual(html.count('class="native-file-input"'), 3)
        self.assertNotIn("operation-overlay", html)

    def test_ui_uses_queue_endpoints_instead_of_direct_transcription(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
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
        self.assertIn('"/api/url-download/settings"', app_js)
        self.assertIn('"/api/frames/settings"', app_js)
        self.assertIn('"/api/ocr/status"', app_js)
        self.assertIn('"/api/ocr/check"', app_js)
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
        self.assertIn("loadTranscript(file.path || file.name, true, true)", app_js)
        self.assertIn('transcriptText.value = result.text || "";', app_js)
        self.assertIn("queueItemTranscriptPath", app_js)
        self.assertIn("pathLooksLikeQueueTranscript", app_js)
        self.assertIn("maybeLoadLatestStorageTranscript", app_js)
        self.assertIn("frameRateOptions", app_js)
        self.assertIn("data-queue-operation", app_js)
        self.assertIn("data-queue-frame-rate", app_js)
        self.assertIn("data-queue-jpeg-quality", app_js)
        self.assertIn("data-queue-frame-size", app_js)
        self.assertIn("data-queue-url-max-height", app_js)
        self.assertIn("data-queue-settings-panel", app_js)
        self.assertIn("75, 80, 85, 90, 95, 100", app_js)
        self.assertIn("frameMaxSizeOptions", app_js)
        self.assertIn("urlDownloadMaxVideoHeightOptions", app_js)
        self.assertIn("max_frame_size", app_js)
        self.assertIn("max_video_height", app_js)
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
        self.assertIn("queueFolderNameValue", app_js)
        self.assertIn("queue_folder_name", app_js)
        self.assertIn("queueFolderNameInput.disabled = queueActive || hasAddingInProgress() || Boolean(status?.queue_path);", app_js)
        self.assertIn("const queueFolderLocked = Boolean(latestQueueStatus?.queue_path);", app_js)
        self.assertNotIn(
            "Number(latestQueueStatus?.total_items || 0) > 0 || Boolean(latestQueueStatus?.queue_path)",
            app_js,
        )
        self.assertNotIn("queueSettingsSummary", html)
        self.assertNotIn("queueSnapshot", app_js)
        self.assertIn("queueFolderArtifactPath", app_js)
        self.assertIn("queueManifestArtifactPath", app_js)
        self.assertIn("queueItemFolderArtifactPath", app_js)
        self.assertIn("sourceManifestArtifactPath", app_js)
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
        self.assertIn("collapsedQueueSettingsItemIds", app_js)
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
        self.assertIn('<details id="defaultProcessingSettings" class="default-processing-settings settings-collapsible" aria-labelledby="defaultProcessingSettingsTitle" open>', html)
        self.assertIn('<summary class="default-processing-heading settings-collapsible-summary">', html)
        default_settings_html = html[
            html.index('id="defaultProcessingSettings"'):html.index('id="queueOutput"')
        ]
        self.assertIn('<details id="defaultAudioFramesSettings" class="default-settings-subsection settings-collapsible" open>', html)
        self.assertIn('<details id="defaultUrlDownloadSettings" class="default-settings-subsection settings-collapsible">', html)
        self.assertIn('<details id="defaultOcrSettings" class="default-settings-subsection settings-collapsible">', html)
        self.assertIn('<details id="defaultCvSettings" class="default-settings-subsection settings-collapsible">', html)
        for element_id in (
            "defaultProcessingSettings",
            "defaultAudioFramesSettings",
            "defaultUrlDownloadSettings",
            "defaultOcrSettings",
            "defaultCvSettings",
            "defaultAudioEnabled",
            "defaultFramesEnabled",
            "defaultOcrEnabled",
            "defaultOcrTesseract",
            "defaultOcrPaddle",
            "defaultOcrWindows",
            "defaultCvMetadataEnabled",
            "defaultCvObjectDetection",
            "defaultCvVlmAnalysis",
            "defaultCvYoloObjectDetection",
            "defaultFrameRateSelect",
            "defaultJpegQualitySelect",
            "defaultFrameMaxSizeSelect",
        ):
            self.assertIn(f'id="{element_id}"', html)
        for key in (
            "defaultProcessingSettingsTitle",
            "audioFramesSettingsTitle",
            "appliesToNewQueueItems",
            "itemSettingsOverrideDefaults",
            "itemProcessingSettings",
            "processingPlan",
            "processingPlanAudio",
            "processingPlanFrames",
            "processingPlanOcr",
            "processingPlanCv",
            "cvSettingsTitle",
            "ocrEasyOcrOption",
            "ocrTesseractSoon",
            "ocrPaddleSoon",
            "ocrWindowsSoon",
            "ocrEasyOcrUnavailable",
            "visualMetadata",
            "cvObjectDetectionSoon",
            "cvVlmAnalysisSoon",
            "cvYoloObjectDetectionSoon",
            "cvMetadataRequiresFrames",
            "disabled",
            "comingSoon",
        ):
            self.assertIn(key, html + app_js)
        self.assertNotIn("placeholder-fieldset", default_settings_html)
        self.assertIn('id="defaultOcrEnabled"', default_settings_html)
        self.assertIn('data-i18n="ocrEasyOcrOption"', default_settings_html)
        self.assertIn('data-i18n="cvSettingsTitle"', default_settings_html)
        audio_frames_html = html[
            html.index('id="defaultAudioFramesSettings"'):html.index('id="defaultUrlDownloadSettings"')
        ]
        self.assertNotIn('id="defaultOcrEnabled"', audio_frames_html)
        self.assertNotIn('data-i18n="ocr"', audio_frames_html)
        self.assertIn("defaultProcessingPlanSnapshot", app_js)
        self.assertIn("processingPlanForQueueItem", app_js)
        self.assertIn("processing_plan", app_js)
        self.assertIn("frameMaxSizeLabel(plan.frames.max_frame_size)", app_js)
        self.assertIn('optionGroup.className = "queue-options queue-options-collapsible"', app_js)
        self.assertIn('optionGroup.open = !collapsedQueueSettingsItemIds.has(queueItem.index)', app_js)
        self.assertIn("optionSummary.append(label, createProcessingPlanSummary(queueItem))", app_js)
        self.assertIn(".settings-collapsible-summary::before", css := (STATIC_DIR / "style.css").read_text(encoding="utf-8"))
        self.assertIn('.queue-options-collapsible[open] > .settings-collapsible-summary::before', css)
        self.assertIn("defaultOcrEnabled.checked && !defaultOcrEnabled.disabled", app_js)
        self.assertIn('ocrBackend: "easyocr"', app_js)
        self.assertIn("ocrEngineAvailable: easyOcrActionable()", app_js)
        self.assertIn("defaultCvMetadataEnabled.checked && !defaultCvMetadataEnabled.disabled", app_js)
        self.assertIn("const normalizedFramesEnabled = Boolean(framesEnabled) || normalizedOcrEnabled;", app_js)
        self.assertIn("input.disabled = true", app_js)
        self.assertNotIn("Tesseract OCR (coming soon)", app_js)
        self.assertNotIn("Basic OpenCV (coming soon)", app_js)

    def test_header_and_ocr_cv_checkbox_contract(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertNotIn('id="modelBadge"', html)
        self.assertNotIn('id="appVersion"', html)
        self.assertNotIn("modelBadge", app_js)
        self.assertNotIn("appVersion", app_js)
        self.assertNotIn("Version: local-dev", html + app_js)
        self.assertNotIn("Whisper tiny", html + app_js)

        ocr_section = html[html.index('id="defaultOcrSettings"'):html.index('id="defaultCvSettings"')]
        cv_section = html[html.index('id="defaultCvSettings"'):html.index('</details>', html.index('id="defaultCvSettings"'))]
        audio_frames_section = html[html.index('id="defaultAudioFramesSettings"'):html.index('id="defaultUrlDownloadSettings"')]
        self.assertNotIn("<select", ocr_section)
        self.assertNotIn('type="radio"', ocr_section + cv_section)
        self.assertIn('id="defaultOcrEnabled" type="checkbox"', ocr_section)
        self.assertIn('id="defaultCvMetadataEnabled" type="checkbox"', cv_section)
        for element_id in ("defaultOcrTesseract", "defaultOcrPaddle", "defaultOcrWindows"):
            self.assertIn(f'id="{element_id}" type="checkbox" disabled', ocr_section)
        for element_id in ("defaultCvObjectDetection", "defaultCvVlmAnalysis", "defaultCvYoloObjectDetection"):
            self.assertIn(f'id="{element_id}" type="checkbox" disabled', cv_section)
        self.assertNotIn('id="defaultOcrEnabled"', audio_frames_section)
        self.assertNotIn('data-i18n="ocr"', audio_frames_section)
        self.assertNotIn('name="ocr', ocr_section)
        self.assertNotIn('name="cv', cv_section)

    def test_ocr_ui_reports_easyocr_readiness_and_frame_artifacts(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="ocrSettingsPanel"', html)
        self.assertIn('id="defaultOcrEnabled"', html)
        self.assertIn('type="checkbox" disabled', html[html.index('id="defaultOcrEnabled"') - 80:html.index('id="defaultOcrEnabled"') + 120])
        for element_id, key in (
            ("defaultOcrTesseract", "ocrTesseractSoon"),
            ("defaultOcrPaddle", "ocrPaddleSoon"),
            ("defaultOcrWindows", "ocrWindowsSoon"),
        ):
            self.assertIn(f'id="{element_id}" type="checkbox" disabled', html)
            self.assertIn(f'data-i18n="{key}"', html)
        self.assertIn('data-i18n="ocrNextStage"', html)
        self.assertIn("function createOcrPlanSettings(queueItem, disabled)", app_js)
        self.assertNotIn('createComingSoonOption("ocr")', app_js)
        self.assertIn("function createCvPlanSettings(queueItem, disabled)", app_js)
        self.assertNotIn('createComingSoonOption("cv")', app_js)
        self.assertNotIn('"queueOcrBackend"', app_js)
        self.assertNotIn("[data-queue-ocr-backend]", app_js)
        self.assertIn("resolved_backend", app_js)
        self.assertIn("engine_available: backendAvailable", app_js)
        self.assertIn("status?.backends?.easyocr", app_js)
        self.assertIn("easyOcrActionable()", app_js)
        self.assertIn('setLocalizedOutput(ocrStatusMessage, "ocrReadyForProcessing"', app_js)
        self.assertIn('setLocalizedOutput(ocrStatusMessage, "ocrEasyOcrUnavailable"', app_js)
        self.assertIn('t("ocrRunsOnExtractedFrames")', app_js)
        self.assertIn("outputs.ocr_jsonl_path", app_js)
        self.assertIn("outputs.ocr_txt_path", app_js)
        self.assertIn("outputs.cv_jsonl_path", app_js)
        self.assertIn("outputs.cv_txt_path", app_js)
        self.assertNotIn("ocrTesseractFields.hidden", app_js)
        self.assertNotIn("selected_backend: ocrBackendSelect.value", app_js)
        self.assertIn('const selectedOcrBackend = "easyocr"', app_js)
        self.assertIn('languages: ocrLanguages || (backend === "tesseract" ? ["rus", "eng"] : ["ru", "en"])', app_js)
        self.assertIn("queueStageOcrProcessing", app_js)
        self.assertIn("statusOcrProcessing", app_js)
        self.assertIn("queueStageCvProcessing", app_js)
        self.assertIn("statusCvProcessing", app_js)

    def test_url_download_profile_ui_and_plan_snapshot_contract(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="urlDownloadSettingsPanel"', html)
        for profile in (
            "auto",
            "best_for_extraction",
            "best_quality",
            "smallest_file",
            "prefer_webm",
            "prefer_mp4",
            "prefer_mkv",
            "prefer_mov",
            "prefer_avi",
            "audio_friendly",
            "custom",
        ):
            self.assertIn(f'value="{profile}"', html)
        self.assertIn('id="urlDownloadCustomField"', html)
        self.assertIn('id="urlDownloadMaxVideoHeightSelect"', html)
        for height in ("auto", "480", "720", "1080", "1440", "2160"):
            self.assertIn(f'value="{height}"', html)
        self.assertIn("syncUrlDownloadCustomField", app_js)
        self.assertIn("urlDownloadMaxVideoHeightLabel", app_js)
        self.assertIn("createUrlDownloadSettings", app_js)
        self.assertIn("queue-url-settings", app_js)
        self.assertIn('wrapper.hidden = queueItem.source_type !== "url" && queueItem.media_kind !== "url"', app_js)
        self.assertIn("urlDownloadPlan.max_video_height = urlMaxHeightSelect.value", app_js)
        self.assertIn("url_download:", app_js)
        self.assertIn("item.dataset.urlDownload", app_js)
        self.assertIn('setLocalizedOutput(queueOutput, "queueStarted")', app_js)
        self.assertNotIn('setOutput(queueOutput, t("queueStarted"))', app_js)

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
        self.assertIn("openRuntimeEstimateDetailsKeys", app_js)
        self.assertIn("runtimeEstimateDetailsKey(queueItem, status)", app_js)
        self.assertIn("details.dataset.runtimeEstimateDetailsKey = detailsKey", app_js)
        self.assertIn("details.open = openRuntimeEstimateDetailsKeys.has(detailsKey)", app_js)
        self.assertIn("estimateDetails", app_js)
        self.assertIn("estimateBreakdownHeading", app_js)
        self.assertIn("estimateTranscriptionBreakdown", app_js)
        self.assertIn("estimateFrameExtractionBreakdown", app_js)
        self.assertIn("estimateOcrBreakdown", app_js)
        self.assertIn("estimateOcrExpectedFrames", app_js)
        self.assertIn("estimateOcrSampledFrames", app_js)
        self.assertIn("estimateOcrAveragePerFrame", app_js)
        self.assertIn("audioEstimateUnavailableMessage", app_js)
        self.assertIn("estimateAudioUnavailableSummary", app_js)
        self.assertIn("estimateAudioNoStream", app_js)
        self.assertIn("estimateAudioTotalExcluded", app_js)
        self.assertIn("total_excludes_audio", app_js)
        self.assertIn("estimateOcrTotalExcluded", app_js)
        self.assertIn("noEnabledOperationsEstimate", app_js)
        self.assertIn("createOcrPlanSettings(queueItem, controlsDisabled)", app_js)
        self.assertIn("createCvPlanSettings(queueItem, controlsDisabled)", app_js)
        self.assertIn(".queue-runtime-estimate", css)
        self.assertIn(".queue-estimate-button", css)

    def test_queue_stage_progress_and_download_cancel_contract_exist(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        css = (STATIC_DIR / "style.css").read_text(encoding="utf-8")

        self.assertIsNone(re.search(r"[А-Яа-яЁё]", app_js))
        self.assertIsNone(re.search(r"[А-Яа-яЁё]", html))
        self.assertIn("function createQueueStageProgress(queueItem)", app_js)
        self.assertIn("queueItem.stage_progress", app_js)
        self.assertIn('bar.removeAttribute("value")', app_js)
        self.assertIn('wrapper.dataset.progressMode = progress.mode', app_js)
        self.assertIn("queueStageCancellingDownload", app_js)
        self.assertIn("queueStageDownloadCancelled", app_js)
        self.assertIn("queueStageDownloadFailed", app_js)
        self.assertIn('t("cancelDownload")', app_js)
        self.assertIn(".queue-item-stage-progress", css)
        self.assertIn("transition: width 220ms ease", css)
        self.assertIn("function renderModelDownloadStatus(status)", app_js)
        self.assertIn('id="modelDownloadProgress"', html)

    def test_processing_plan_polish_contract(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")

        self.assertNotIn('id="transcriptionSettings"', html)
        self.assertNotIn('data-i18n="settingsTitle"', html)
        self.assertNotIn('data-i18n="settingsNote"', html)
        self.assertNotIn("Настройки транскрибации", html)
        self.assertNotIn('data-i18n="maxFrameSizeHelp"', html)
        self.assertNotIn("maxFrameSizeHelp", i18n)
        self.assertNotIn(
            "Уменьшает сохраняемые кадры без изменения пропорций. Полезно для ускорения OCR/CV и уменьшения размера файлов.",
            i18n,
        )
        self.assertNotIn(
            "Downscales saved frames without changing aspect ratio. Useful for faster OCR/CV and smaller files.",
            i18n,
        )
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
        self.assertIn('"cancellingDownload"', app_js)
        self.assertIn(': "cancelling",', app_js)
        self.assertIn('t("cancelRequestSent")', app_js)

    def test_queue_adds_snapshot_default_processing_plan_before_disabling_controls(self) -> None:
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

        recordings_start = app_js.index("async function addRecordingsToQueue")
        recordings_snapshot = app_js.index("const processingPlan = defaultProcessingPlanSnapshot();", recordings_start)
        recordings_disabled = app_js.index("isAddingRecording = true;", recordings_start)
        self.assertLess(recordings_snapshot, recordings_disabled)
        self.assertIn("processing_plan: processingPlan,", app_js[recordings_start:])

        files_start = app_js.index("async function addLocalFilesToQueue")
        files_snapshot = app_js.index("const processingPlan = defaultProcessingPlanSnapshot();", files_start)
        files_disabled = app_js.index("isAddingFile = true;", files_start)
        self.assertLess(files_snapshot, files_disabled)
        self.assertIn('formData.append("processing_plan", JSON.stringify(processingPlan));', app_js[files_start:])

        urls_start = app_js.index('queueUrlForm.addEventListener("submit"')
        urls_snapshot = app_js.index("const processingPlan = defaultProcessingPlanSnapshot();", urls_start)
        urls_disabled = app_js.index("isAddingUrl = true;", urls_start)
        self.assertLess(urls_snapshot, urls_disabled)
        self.assertIn("processing_plan: processingPlan", app_js[urls_start:])

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
        self.assertIn('<details id="transcriptPreviewSection" class="transcript-preview collapsible-section">', html)
        self.assertNotIn('<details id="transcriptPreviewSection" class="transcript-preview collapsible-section" open>', html)
        self.assertIn('data-i18n="transcriptFilePathLabel"', html)
        self.assertIn('data-i18n="showTranscriptFile"', html)
        self.assertIn('data-i18n="latestTranscription"', html)
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
