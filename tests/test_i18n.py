import re
import unittest
from pathlib import Path


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def dictionary_keys(content: str, language: str) -> set[str]:
    if language == "ru":
        block = content.split("ru: {", 1)[1].split("    en: {", 1)[0]
    else:
        block = content.split("    en: {", 1)[1].split("  };", 1)[0]
    return set(re.findall(r"^\s{6}([A-Za-z][A-Za-z0-9_]*):", block, flags=re.MULTILINE))


def dictionary_value(content: str, language: str, key: str) -> str:
    if language == "ru":
        block = content.split("ru: {", 1)[1].split("    en: {", 1)[0]
    else:
        block = content.split("    en: {", 1)[1].split("  };", 1)[0]
    match = re.search(rf"^\s{{6}}{re.escape(key)}:\s*\"([^\"]*)\",", block, flags=re.MULTILINE)
    if not match:
        raise AssertionError(f"{key} missing from {language} dictionary")
    return match.group(1)


class I18nTests(unittest.TestCase):
    def test_ru_en_dictionary_keys_match_and_default_language_is_preserved(self) -> None:
        content = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
        self.assertIn('const DEFAULT_LANGUAGE = "ru"', content)
        self.assertIn('const STORAGE_KEY = "latUiLanguage"', content)
        ru_keys = dictionary_keys(content, "ru")
        en_keys = dictionary_keys(content, "en")
        self.assertEqual(ru_keys, en_keys)
        for key in (
            "transcriptionTitle",
            "addLatestMic",
            "startProcessing",
            "clearGlobalQueue",
            "chooseFile",
            "noFileSelected",
            "tourSourcesText",
            "refreshMicDevices",
            "refreshOutputDevices",
            "micDevicesUpdated",
            "outputDevicesUpdated",
            "refreshMicDevicesFailed",
            "refreshOutputDevicesFailed",
            "micLevelInactive",
            "systemLevelInactive",
            "microphoneSwitched",
            "outputDeviceSwitched",
            "microphoneSwitchFailed",
            "outputDeviceSwitchFailed",
            "screenSource",
            "mouseSource",
            "keyboardSource",
            "inputSourcesScreenRequired",
            "keyboardPrivacyHint",
            "displays",
            "displayFound",
            "displaysFound",
            "displayOption",
            "selectDisplaysToRecord",
            "screenCardLabel",
            "displayResolution",
            "displayResolutionValue",
            "displayCoordinates",
            "displayCoordinatesValue",
            "displayMonitorIndex",
            "showPreview",
            "hidePreview",
            "refreshPreview",
            "previewUnavailable",
            "previewOffByDefault",
            "previewLoading",
            "previewRefreshed",
            "previewAlt",
            "screenFps",
            "selectDisplayToRecord",
            "screenRecordingStarted",
            "screenRecordingStopped",
            "mediaSessionSaved",
            "recordingsSavedTo",
            "screenTimingWarning",
            "screenTimingDiagnostic",
            "screenCursorWarning",
            "mouseEventsFile",
            "keyboardEventsFile",
            "inputEventLoggingFailed",
            "videoMuxTitle",
            "videoMuxSelectVideo",
            "videoMuxSelectMic",
            "videoMuxSelectSystem",
            "videoMuxStarted",
            "videoMuxCompleted",
            "videoMuxFailed",
            "recentRecordings",
            "helpDeviceSummary",
            "helpSystemOutputText",
            "helpScreenTitle",
            "helpScreenText",
            "helpDeviceNamesText",
            "helpLoopbackLimitText",
            "helpPlaceholdersText",
            "helpSilentSystemTitle",
            "helpSilentSystemWindows",
            "helpSilentSystemMeetingApp",
            "helpSilentSystemSameDevice",
            "helpSilentSystemRefresh",
            "helpSilentSystemTryAnother",
            "helpSilentSystemRuntime",
            "helpOwnVoiceText",
            "whisperModelsTitle",
            "modelManagerModel",
            "downloadModel",
            "verifyModel",
            "deleteModel",
            "defaultSuffix",
            "defaultProcessingSettingsTitle",
            "appliesToNewQueueItems",
            "itemSettingsOverrideDefaults",
            "processingPlan",
            "processingPlanAudio",
            "processingPlanFrames",
            "processingPlanOcr",
            "processingPlanCv",
            "estimateTime",
            "estimating",
            "estimateComplete",
            "estimateFailed",
            "runtimeEstimate",
            "estimateDetails",
            "sampleSegment",
            "sampleRuntime",
            "estimatedFullTime",
            "totalEstimate",
            "estimateAudioSummary",
            "estimateFramesSummary",
            "estimateAudioConfig",
            "estimateFramesConfig",
            "sampleFrames",
            "estimatedTotalFrames",
            "estimateSpeed",
            "approximateEstimate",
            "noEnabledOperationsEstimate",
            "estimateDurationUnavailable",
            "estimateUrlDownloadRequired",
            "estimateFfmpegUnavailable",
            "estimateSamplePreparationFailed",
            "estimateSourceUnavailable",
            "estimateAboutDuration",
            "durationSecondsShort",
            "durationMinutesShort",
            "durationHoursShort",
            "audio",
            "frames",
            "ocr",
            "cv",
            "computerVision",
            "frameInterval",
            "jpegQuality",
            "maxFrameSize",
            "maxFrameSizeOriginal",
            "maxFrameSizeWidth1920",
            "maxFrameSizeWidth1280",
            "maxFrameSizeWidth960",
            "maxFrameSizeWidth640",
            "maxFrameSizeHelp",
            "disabled",
            "comingSoon",
            "ocrEngineComingSoon",
            "cvEngineComingSoon",
            "ocrEnginePlaceholder",
            "ocrLanguagePlaceholder",
            "cvEnginePlaceholder",
            "selectAtLeastOneAudioOperation",
            "modelStatusAvailable",
            "modelStatusReady",
            "modelStatusStarting",
            "modelStatusNotDownloaded",
            "modelStatusDownloading",
            "modelStatusVerifying",
            "modelStatusFailed",
            "modelStatusDownloadError",
            "modelStatusVerificationError",
            "modelDownloadStarting",
            "modelDownloadProgressCleared",
            "modelDeleteConfirm",
            "modelInfoOrigin",
            "modelInfoSmallPositioning",
            "modelInfoLargeV3Hardware",
            "tourModelsTitle",
            "tourModelsText",
            "show",
            "hide",
            "processingOptions",
            "itemProcessingSettings",
            "transcribeAudio",
            "extractFrames",
            "urlMedia",
            "ocr",
            "cv",
            "comingSoon",
            "frameExtractionRate",
            "jpegQuality",
            "estimatedFrames",
            "frameEstimateAfterDownload",
            "frameCountWarning",
            "downloadedMediaResultPath",
            "mediaDownloadFailed",
            "mediaDownloadTimedOut",
            "mediaDownloadNeedsAuth",
            "transcriptResultPath",
            "partialTranscriptArtifactPath",
            "framesResultFolder",
            "framesResultCount",
            "framesResultIndex",
            "removeFromQueue",
            "cancelCurrentItem",
            "cancelDownload",
            "cancellingDownload",
            "cancelCurrentShort",
            "cancelTranscription",
            "cancellingTranscription",
            "cancelRequestSent",
            "cancelling",
            "transcriptionCancelled",
            "transcriptionCancelAfterSegment",
            "runningItemCannotCancel",
            "frameWriteError",
            "selectAtLeastOneUrlOperation",
            "statusExtractingFrames",
            "statusNotApplicable",
            "statusIdle",
            "statusTranscribingAudio",
            "queueStageStatusIdle",
            "queueStageStatusRunning",
            "queueStageStatusRunningProgress",
            "queueItemStatusLine",
            "queueItemStageLine",
            "queueStageAddingFile",
            "queueStageAddingUrl",
            "queueStageWaitingDownload",
            "queueFileAlreadyAdding",
            "queueUrlAlreadyAdding",
            "queueFileAlreadyQueued",
            "queueUrlAlreadyQueued",
            "queueStageIdle",
            "queueStagePreparingSource",
            "queueStageDownloadingMedia",
            "queueStageDownloadingVideo",
            "queueStageCancellingDownload",
            "queueStageDownloadCancelled",
            "queueStageDownloadFailed",
            "queueStageTranscribingAudio",
            "queueStageExtractingFrames",
            "queueStageCancellingTranscription",
            "queueStageCancelling",
            "queueStageCompleted",
            "queueStageFailed",
            "queueStageCancelled",
            "queueStageOcrFuture",
            "queueStageCvFuture",
            "queueStageMediaIndexFuture",
            "downloadProgress",
            "stageProgress",
            "downloadedAmount",
            "downloadSize",
            "downloadSpeed",
            "downloadEta",
            "stageProgressPercent",
            "stageProgressUnits",
            "working",
            "progressUnavailable",
            "storageTitle",
            "storageNote",
            "storageTotalSize",
            "storageDownloads",
            "storageUploads",
            "storageRecordings",
            "storageTranscripts",
            "storageLogs",
            "storageJobs",
            "storageFolder",
            "refreshStorageSizes",
            "openDataFolder",
            "storageSettingsTitle",
            "keepDownloadedUrlMedia",
            "keepUploadedTempFiles",
            "storageConservativeNote",
            "storageSettingsSaved",
            "storageCleanupTitle",
            "clearDownloads",
            "clearUploads",
            "confirmClearDownloads",
            "confirmClearUploads",
            "cleanupCompleted",
            "cleanupFailed",
            "cleanupPartial",
            "outputArtifactsTitle",
            "transcriptArtifactPath",
            "diagnosticJsonArtifactPath",
            "framesArtifactPath",
            "framesIndexArtifactPath",
            "downloadedMediaArtifactPath",
            "downloadedMediaDeleted",
            "uploadedTempArtifactPath",
            "uploadedTempDeleted",
            "artifactPathMissing",
            "artifactCleanupError",
            "noFilesCreated",
        ):
            self.assertIn(key, en_keys)

    def test_html_and_dynamic_i18n_keys_exist_in_both_dictionaries(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        app_js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        keys = dictionary_keys(i18n, "en")
        html_keys = set(re.findall(r'data-i18n(?:-title|-aria-label|-placeholder)?="([A-Za-z][A-Za-z0-9_]*)"', html))
        app_keys = set(re.findall(r'(?<![A-Za-z0-9_$])t\("([A-Za-z][A-Za-z0-9_]*)"', app_js))
        self.assertFalse((html_keys | app_keys) - keys)

    def test_processing_plan_polish_copy_is_localized(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")

        expected = {
            "audio": ("Аудио", "Audio"),
            "statusNotApplicable": ("Не применяется", "Not applicable"),
            "statusIdle": ("Ожидание", "Idle"),
            "statusExtractingFrames": ("Извлечение кадров", "Extracting frames"),
            "statusTranscribingAudio": ("Транскрибация аудио", "Transcribing audio"),
            "cancelRequestSent": ("Запрос на отмену отправлен...", "Cancel request sent..."),
            "cancelling": ("Отмена выполняется...", "Cancelling..."),
            "modelOptionTiny": ("самая быстрая, минимальное качество", "fastest, lowest quality"),
            "modelOptionBase": ("быстрая, базовое качество", "fast, basic quality"),
            "modelOptionSmall": ("баланс скорости и качества", "balanced speed and quality"),
            "modelOptionMedium": ("выше качество, медленнее", "higher quality, slower"),
            "modelOptionLargeV3": ("лучшее качество, тяжелая модель", "best quality, heavy model"),
        }
        for key, (ru_value, en_value) in expected.items():
            self.assertEqual(ru_value, dictionary_value(i18n, "ru", key))
            self.assertEqual(en_value, dictionary_value(i18n, "en", key))

        self.assertEqual("Параметры обработки элемента", dictionary_value(i18n, "ru", "itemProcessingSettings"))
        self.assertEqual("Item processing settings", dictionary_value(i18n, "en", "itemProcessingSettings"))

    def test_storage_settings_saved_message_is_localized(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")

        self.assertEqual("Настройки хранения сохранены.", dictionary_value(i18n, "ru", "storageSettingsSaved"))
        self.assertEqual("Storage settings saved.", dictionary_value(i18n, "en", "storageSettingsSaved"))
        self.assertIn('"Настройки хранения сохранены.": "Storage settings saved."', i18n)

    def test_ocr_settings_copy_is_localized(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
        ru_keys = dictionary_keys(i18n, "ru")
        en_keys = dictionary_keys(i18n, "en")
        for key in (
            "ocrSettingsTitle",
            "ocrEngineLabel",
            "ocrEngineTesseract",
            "ocrEngineEasyOcr",
            "ocrEnginePaddleOcr",
            "ocrEngineWindowsOcr",
            "ocrSelectedBackend",
            "ocrBackendTypeLabel",
            "ocrTypeExternalExecutable",
            "ocrTypeIntegratedOptional",
            "ocrTypeOptionalExperimental",
            "ocrTypeWindowsExperimental",
            "ocrPathLabel",
            "ocrVersionLabel",
            "ocrLanguagesLabel",
            "ocrCustomPathLabel",
            "ocrCustomPathPlaceholder",
            "ocrCheckButton",
            "ocrSaveButton",
            "ocrChecking",
            "ocrStatusAvailable",
            "ocrStatusNotFound",
            "ocrStatusNotInstalled",
            "ocrStatusUnsupportedPlatform",
            "ocrStatusCheckFailed",
            "ocrBackendAvailable",
            "ocrBackendNotAvailable",
            "ocrHasRus",
            "ocrMissingRus",
            "ocrHasEng",
            "ocrMissingEng",
            "ocrInstallHint",
            "ocrOptionalDependenciesMissing",
            "ocrEasyOcrMissing",
            "ocrExperimentalNote",
            "ocrWindowsOnlyNote",
            "ocrWindowsExperimentalNote",
            "ocrEnginesChecked",
            "ocrSettingsSaved",
            "ocrNextStage",
            "ocrErrorInvalidPath",
        ):
            self.assertIn(key, ru_keys)
            self.assertIn(key, en_keys)
        self.assertEqual("OCR / text recognition", dictionary_value(i18n, "en", "ocrSettingsTitle"))
        self.assertEqual(
            "At this stage the app only checks OCR engines. Text recognition on frames will be added in the next stage.",
            dictionary_value(i18n, "en", "ocrNextStage"),
        )

    def test_url_download_settings_copy_is_localized(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
        ru_keys = dictionary_keys(i18n, "ru")
        en_keys = dictionary_keys(i18n, "en")
        for key in (
            "urlDownloadSettingsTitle",
            "urlDownloadSettingsHelp",
            "urlDownloadProfileLabel",
            "urlDownloadProfileAuto",
            "urlDownloadProfileBestForExtraction",
            "urlDownloadProfileBestQuality",
            "urlDownloadProfileSmallestFile",
            "urlDownloadProfilePreferWebm",
            "urlDownloadProfilePreferMp4",
            "urlDownloadProfilePreferMkv",
            "urlDownloadProfilePreferMov",
            "urlDownloadProfilePreferAvi",
            "urlDownloadProfileAudioFriendly",
            "urlDownloadProfileCustom",
            "urlDownloadMaxVideoHeightLabel",
            "urlDownloadMaxVideoHeightAuto",
            "urlDownloadMaxVideoHeight480",
            "urlDownloadMaxVideoHeight720",
            "urlDownloadMaxVideoHeight1080",
            "urlDownloadMaxVideoHeight1440",
            "urlDownloadMaxVideoHeight2160",
            "urlDownloadMaxVideoHeightHelp",
            "urlDownloadCustomFormatLabel",
            "urlDownloadLogMediaProbe",
            "urlDownloadLogExtractionBenchmark",
            "urlDownloadSettingsSaved",
            "urlDownloadCustomFallback",
            "frameSettingsSaved",
            "processingPlanUrlDownload",
        ):
            self.assertIn(key, ru_keys)
            self.assertIn(key, en_keys)
        self.assertEqual("Prefer WebM", dictionary_value(i18n, "en", "urlDownloadProfilePreferWebm"))
        self.assertEqual("Max URL video resolution", dictionary_value(i18n, "en", "urlDownloadMaxVideoHeightLabel"))
        self.assertEqual("Up to 2160p / 4K", dictionary_value(i18n, "en", "urlDownloadMaxVideoHeight2160"))

    def test_idle_level_messages_are_localized(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")

        self.assertEqual("Микрофон активен только во время записи.", dictionary_value(i18n, "ru", "micLevelInactive"))
        self.assertEqual("The microphone is active only during recording.", dictionary_value(i18n, "en", "micLevelInactive"))
        self.assertEqual(
            "Индикатор системного звука активен только во время записи.",
            dictionary_value(i18n, "ru", "systemLevelInactive"),
        )
        self.assertEqual(
            "System audio level is active only during recording.",
            dictionary_value(i18n, "en", "systemLevelInactive"),
        )

    def test_queue_start_action_uses_processing_label(self) -> None:
        i18n = (STATIC_DIR / "i18n.js").read_text(encoding="utf-8")
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        self.assertIn('data-i18n="startProcessing"', html)
        self.assertIn('startProcessing: "Запустить обработку"', i18n)
        self.assertIn('startProcessing: "Start processing"', i18n)
        self.assertNotIn('data-i18n="startTranscription"', html)
        self.assertNotIn('Start transcription"', i18n)
        self.assertNotIn('Запустить транскрибацию"', i18n)

    def test_user_facing_static_markup_and_app_logic_do_not_embed_russian(self) -> None:
        for filename in ("index.html", "app.js", "tour.js"):
            content = (STATIC_DIR / filename).read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"[А-Яа-яЁё]", content), filename)


if __name__ == "__main__":
    unittest.main()
