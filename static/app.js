const startRecordButton = document.querySelector("#startRecordButton");
const stopRecordButton = document.querySelector("#stopRecordButton");
const refreshMicDevicesButton = document.querySelector("#refreshMicDevicesButton");
const refreshOutputDevicesButton = document.querySelector("#refreshOutputDevicesButton");
const micSourceCheckbox = document.querySelector("#micSourceCheckbox");
const systemSourceCheckbox = document.querySelector("#systemSourceCheckbox");
const screenSourceCheckbox = document.querySelector("#screenSourceCheckbox");
const mouseSourceCheckbox = document.querySelector("#mouseSourceCheckbox");
const keyboardSourceCheckbox = document.querySelector("#keyboardSourceCheckbox");
const inputSourceHint = document.querySelector("#inputSourceHint");
const recordingSourceCheckboxes = [micSourceCheckbox, systemSourceCheckbox, screenSourceCheckbox, mouseSourceCheckbox, keyboardSourceCheckbox];
const micDeviceRow = document.querySelector("#micDeviceRow");
const systemDeviceRow = document.querySelector("#systemDeviceRow");
const screenControls = document.querySelector("#screenControls");
const displayFoundSummary = document.querySelector("#displayFoundSummary");
const displayList = document.querySelector("#displayList");
const screenFpsSelect = document.querySelector("#screenFpsSelect");
const screenOutput = document.querySelector("#screenOutput");
const micDeviceSelect = document.querySelector("#micDeviceSelect");
const outputDeviceSelect = document.querySelector("#outputDeviceSelect");
const recordingState = document.querySelector("#recordingState");
const recordingOutput = document.querySelector("#recordingOutput");
const micLevelBlock = document.querySelector("#micLevelBlock");
const systemLevelBlock = document.querySelector("#systemLevelBlock");
const micLevelMeterFill = document.querySelector("#micLevelMeterFill");
const micRmsValue = document.querySelector("#micRmsValue");
const micPeakValue = document.querySelector("#micPeakValue");
const micLevelWarning = document.querySelector("#micLevelWarning");
const systemLevelMeterFill = document.querySelector("#systemLevelMeterFill");
const systemRmsValue = document.querySelector("#systemRmsValue");
const systemPeakValue = document.querySelector("#systemPeakValue");
const systemLevelWarning = document.querySelector("#systemLevelWarning");
const recordingTranscribeActions = document.querySelector("#recordingTranscribeActions");
const transcribeMicRecordingButton = document.querySelector("#transcribeMicRecordingButton");
const transcribeSystemRecordingButton = document.querySelector("#transcribeSystemRecordingButton");
const transcribeAllRecordingsButton = document.querySelector("#transcribeAllRecordingsButton");
const transcribeForm = document.querySelector("#transcribeForm");
const audioFileInput = document.querySelector("#audioFileInput");
const audioFilePickerButton = document.querySelector("#audioFilePickerButton");
const audioFilePickerText = document.querySelector("#audioFilePickerText");
const whisperModelSelect = document.querySelector("#whisperModelSelect");
const whisperDeviceSelect = document.querySelector("#whisperDeviceSelect");
const deviceAvailabilityOutput = document.querySelector("#deviceAvailabilityOutput");
const modelAvailabilityOutput = document.querySelector("#modelAvailabilityOutput");
const modelDownloadWarning = document.querySelector("#modelDownloadWarning");
const refreshModelsButton = document.querySelector("#refreshModelsButton");
const modelManagerStatus = document.querySelector("#modelManagerStatus");
const modelManagerBody = document.querySelector("#modelManagerBody");
const modelDownloadProgressBlock = document.querySelector("#modelDownloadProgressBlock");
const modelDownloadProgress = document.querySelector("#modelDownloadProgress");
const modelDownloadProgressText = document.querySelector("#modelDownloadProgressText");
const modelDownloadProgressNote = document.querySelector("#modelDownloadProgressNote");
const modelInfoPanel = document.querySelector("#modelInfoPanel");
const modelInfoTitle = document.querySelector("#modelInfoTitle");
const modelInfoList = document.querySelector("#modelInfoList");
const modelInfoCloseButton = document.querySelector("#modelInfoCloseButton");
const transcribeButton = document.querySelector("#transcribeButton");
const transcribeOutput = document.querySelector("#transcribeOutput");
const transcribeTechnicalDetails = document.querySelector("#transcribeTechnicalDetails");
const transcribeTechnicalText = document.querySelector("#transcribeTechnicalText");
const benchmarkOutput = document.querySelector("#benchmarkOutput");
const transcriptPreviewSection = document.querySelector("#transcriptPreviewSection");
const transcriptPathForm = document.querySelector("#transcriptPathForm");
const transcriptPathInput = document.querySelector("#transcriptPathInput");
const transcriptPreviewOutput = document.querySelector("#transcriptPreviewOutput");
const transcriptText = document.querySelector("#transcriptText");
const systemStatus = document.querySelector("#systemStatus");
const runtimeDetails = document.querySelector("#runtimeDetails");
const runtimeModel = document.querySelector("#runtimeModel");
const runtimeDevice = document.querySelector("#runtimeDevice");
const runtimeCompute = document.querySelector("#runtimeCompute");
const runtimeSpeed = document.querySelector("#runtimeSpeed");
const recordingsPath = document.querySelector("#recordingsPath");
const transcriptsPath = document.querySelector("#transcriptsPath");
const recordingsFileList = document.querySelector("#recordingsFileList");
const transcriptsFileList = document.querySelector("#transcriptsFileList");
const openRecordingsButton = document.querySelector("#openRecordingsButton");
const openTranscriptsButton = document.querySelector("#openTranscriptsButton");
const storageSummaryGrid = document.querySelector("#storageSummaryGrid");
const refreshStorageSummaryButton = document.querySelector("#refreshStorageSummaryButton");
const openDataFolderButton = document.querySelector("#openDataFolderButton");
const keepDownloadedMediaCheckbox = document.querySelector("#keepDownloadedMediaCheckbox");
const keepUploadedTempCheckbox = document.querySelector("#keepUploadedTempCheckbox");
const clearDownloadsButton = document.querySelector("#clearDownloadsButton");
const clearUploadsButton = document.querySelector("#clearUploadsButton");
const storageCleanupOutput = document.querySelector("#storageCleanupOutput");
const toastRegion = document.querySelector("#toastRegion");
const recordingTimer = document.querySelector("#recordingTimer");
const queueAddForm = document.querySelector("#queueAddForm");
const queueFileInput = document.querySelector("#queueFileInput");
const queueFilePickerButton = document.querySelector("#queueFilePickerButton");
const queueFilePickerText = document.querySelector("#queueFilePickerText");
const queueAddButton = document.querySelector("#queueAddButton");
const queueStartButton = document.querySelector("#queueStartButton");
const queueStopButton = document.querySelector("#queueStopButton");
const queueClearButton = document.querySelector("#queueClearButton");
const queueRetryButton = document.querySelector("#queueRetryButton");
const queueTotal = document.querySelector("#queueTotal");
const queueCompleted = document.querySelector("#queueCompleted");
const queueFailed = document.querySelector("#queueFailed");
const queueCancelled = document.querySelector("#queueCancelled");
const queuePending = document.querySelector("#queuePending");
const queueCurrent = document.querySelector("#queueCurrent");
const queueElapsed = document.querySelector("#queueElapsed");
const queueEta = document.querySelector("#queueEta");
const queueProgress = document.querySelector("#queueProgress");
const queueProgressText = document.querySelector("#queueProgressText");
const queueStageStatus = document.querySelector("#queueStageStatus");
const queueOutput = document.querySelector("#queueOutput");
const queueList = document.querySelector("#queueList");
const queueUrlForm = document.querySelector("#queueUrlForm");
const queueUrlInput = document.querySelector("#queueUrlInput");
const queueUrlAddButton = document.querySelector("#queueUrlAddButton");
const queueFolderNameInput = document.querySelector("#queueFolderNameInput");
const queueFolderPathOutput = document.querySelector("#queueFolderPathOutput");
const defaultAudioEnabled = document.querySelector("#defaultAudioEnabled");
const defaultFramesEnabled = document.querySelector("#defaultFramesEnabled");
const defaultFrameRateSelect = document.querySelector("#defaultFrameRateSelect");
const defaultJpegQualitySelect = document.querySelector("#defaultJpegQualitySelect");
const defaultFrameMaxSizeSelect = document.querySelector("#defaultFrameMaxSizeSelect");
const defaultOcrEnabled = document.querySelector("#defaultOcrEnabled");
const defaultCvMetadataEnabled = document.querySelector("#defaultCvMetadataEnabled");
const urlDownloadProfileSelect = document.querySelector("#urlDownloadProfileSelect");
const urlDownloadMaxVideoHeightSelect = document.querySelector("#urlDownloadMaxVideoHeightSelect");
const urlDownloadCustomField = document.querySelector("#urlDownloadCustomField");
const urlDownloadCustomFormatInput = document.querySelector("#urlDownloadCustomFormatInput");
const urlDownloadLogMediaProbe = document.querySelector("#urlDownloadLogMediaProbe");
const urlDownloadLogExtractionBenchmark = document.querySelector("#urlDownloadLogExtractionBenchmark");
const urlDownloadSaveButton = document.querySelector("#urlDownloadSaveButton");
const urlDownloadSettingsOutput = document.querySelector("#urlDownloadSettingsOutput");
const ocrStatusBadge = document.querySelector("#ocrStatusBadge");
const ocrBackendType = document.querySelector("#ocrBackendType");
const ocrVersion = document.querySelector("#ocrVersion");
const ocrLanguages = document.querySelector("#ocrLanguages");
const ocrCheckButton = document.querySelector("#ocrCheckButton");
const ocrStatusMessage = document.querySelector("#ocrStatusMessage");
const ocrBackendNotes = document.querySelector("#ocrBackendNotes");
const diskFree = document.querySelector("#diskFree");
const operationOverlay = document.querySelector("#operationOverlay");
const operationOverlayTitle = document.querySelector("#operationOverlayTitle");
const operationOverlayText = document.querySelector("#operationOverlayText");
const benchmarkUploadForm = document.querySelector("#benchmarkUploadForm");
const benchmarkFileInput = document.querySelector("#benchmarkFileInput");
const benchmarkFilePickerButton = document.querySelector("#benchmarkFilePickerButton");
const benchmarkFilePickerText = document.querySelector("#benchmarkFilePickerText");
const benchmarkUploadButton = document.querySelector("#benchmarkUploadButton");
const benchmarkStatusOutput = document.querySelector("#benchmarkStatusOutput");
const benchmarkCpuResult = document.querySelector("#benchmarkCpuResult");
const benchmarkCudaResult = document.querySelector("#benchmarkCudaResult");
const benchmarkButtons = Array.from(document.querySelectorAll("[data-benchmark-device]"));
const videoMuxForm = document.querySelector("#videoMuxForm");
const videoMuxVideoSelect = document.querySelector("#videoMuxVideoSelect");
const videoMuxMicSelect = document.querySelector("#videoMuxMicSelect");
const videoMuxSystemSelect = document.querySelector("#videoMuxSystemSelect");
const videoMuxButton = document.querySelector("#videoMuxButton");
const videoMuxOutput = document.querySelector("#videoMuxOutput");

let micLevelPollInFlight = false;
let systemLevelPollInFlight = false;
let lastRecordings = [];
let isTranscribing = false;
let localTranscriptionActive = false;
let isRecording = false;
let modelStatusByName = new Map();
let modelDownloadStatus = null;
let modelDownloadSeenActive = false;
let verifyingModels = new Set();
let deletingModels = new Set();
let modelOperationStatusByName = new Map();
let activeInfoModel = null;
let recordingStartedAtMs = null;
let lastRecordingDurationSec = null;
let queueActive = false;
let previousQueueStatus = "empty";
let latestQueueStatus = null;
let queueControlsFocused = false;
let queueFocusRenderTimer = null;
let isAddingFile = false;
let isAddingUrl = false;
let isAddingRecording = false;
let benchmarkActive = false;
let benchmarkSourceId = null;
let videoMuxInFlight = false;
let overlayOwner = null;
let transcriptionPhase = null;
let activeRuntimeModel = null;
let latestTranscriptionStatus = null;
let latestBenchmarkStatus = null;
let lastLoadedTranscriptPath = null;
let activeMicDeviceValue = "";
let activeOutputDeviceValue = "";
let micDevicesRefreshInFlight = false;
let outputDevicesRefreshInFlight = false;
let displayRefreshInFlight = false;
let displaysLoaded = false;
let latestDisplays = [];
let micSwitchInFlight = false;
let outputSwitchInFlight = false;
let latestRecordingFiles = [];
let latestMicDevicesResult = null;
let latestOutputDevicesResult = null;
let latestOcrStatus = null;
let latestUrlDownloadSettings = {
  format_profile: "auto",
  custom_format: "",
  max_video_height: "auto",
  log_media_probe: true,
  log_extraction_benchmark: true,
};
let latestFrameSettings = {
  max_frame_size: "original",
};
const dynamicOutputRenderers = new Map();
const queueControlSelector = ".queue-item-card select, .queue-item-card input, .queue-item-card button";
const terminalQueueStatuses = new Set(["completed", "error", "failed", "cancelled"]);
const pendingAddKeys = new Set();
const pendingQueueCancellationIds = new Set();
const pendingRuntimeEstimateIds = new Set();
const collapsedQueueSettingsItemIds = new Set();
const openRuntimeEstimateDetailsKeys = new Set();
const audioRuntimeStages = new Set(["transcribing_audio", "cancelling_transcription"]);

function t(key, variables = {}) {
  return window.LATI18N?.t(key, variables) || key;
}

function translateUiText(value) {
  return window.LATI18N?.translateText(value) || value;
}

function showOperation(owner, title, text) {
  overlayOwner = owner;
  operationOverlayTitle.textContent = title;
  operationOverlayText.textContent = text;
  operationOverlay.hidden = false;
}

function hideOperation(owner) {
  if (!owner || overlayOwner === owner) {
    operationOverlay.hidden = true;
    overlayOwner = null;
  }
}

class ApiError extends Error {
  constructor(message, technicalDetails = "") {
    super(message);
    this.name = "ApiError";
    this.technicalDetails = technicalDetails;
  }
}

function setOutput(element, message, type = "info") {
  element.textContent = translateUiText(message);
  element.dataset.type = type;
  dynamicOutputRenderers.delete(element);
}

function setDynamicOutput(element, renderMessage, type = "info") {
  dynamicOutputRenderers.set(element, { renderMessage, type });
  element.textContent = translateUiText(renderMessage());
  element.dataset.type = type;
}

function setLocalizedOutput(element, key, variables = {}, type = "info") {
  setDynamicOutput(element, () => t(key, variables), type);
}

function rerenderDynamicOutputs() {
  for (const [element, state] of dynamicOutputRenderers.entries()) {
    element.textContent = translateUiText(state.renderMessage());
    element.dataset.type = state.type;
  }
}

function setAppState(message, type = "idle") {
  recordingState.textContent = translateUiText(message);
  recordingState.dataset.type = type;
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.dataset.type = type;
  toast.textContent = translateUiText(message);
  toastRegion.append(toast);

  window.setTimeout(() => {
    toast.dataset.hiding = "true";
    window.setTimeout(() => toast.remove(), 180);
  }, 4200);
}

function selectedMicDeviceId() {
  return micDeviceSelect.value === "" ? null : Number(micDeviceSelect.value);
}

function selectedOutputDeviceId() {
  return outputDeviceSelect.value === "" ? null : outputDeviceSelect.value;
}

function selectedDisplayIndices() {
  return Array.from(displayList.querySelectorAll('input[name="screenDisplay"]:checked'))
    .map((input) => Number(input.value))
    .filter((value) => Number.isInteger(value) && value > 0);
}

function displayCardControls() {
  return Array.from(displayList.querySelectorAll('input[name="screenDisplay"], input[name="displayPreview"], button[data-preview-display]'));
}

function selectedScreenFps() {
  return Number(screenFpsSelect.value) || 3;
}

function selectedModel() {
  return whisperModelSelect.value || "small";
}

function selectedDevice() {
  return whisperDeviceSelect.value || "auto";
}

function currentMode() {
  const usesMic = micSourceCheckbox.checked;
  const usesSystem = systemSourceCheckbox.checked;
  if (usesMic && usesSystem) {
    return "both";
  }
  if (usesMic) {
    return "mic";
  }
  if (usesSystem) {
    return "system";
  }
  return null;
}

function setSourcesFromMode(mode) {
  micSourceCheckbox.checked = mode === "mic" || mode === "both";
  systemSourceCheckbox.checked = mode === "system" || mode === "both";
}

function updateFilePickerText(input, target, multiple = false) {
  const files = Array.from(input.files || []);
  if (!files.length) {
    target.textContent = t(multiple ? "noFilesSelected" : "noFileSelected");
    return;
  }

  target.textContent = multiple
    ? t("selectedFilesCount", { count: files.length })
    : files[0].name;
}

function resetFilePicker(input, target, multiple = false) {
  input.value = "";
  updateFilePickerText(input, target, multiple);
}

function fileSuffix(fileName) {
  const match = String(fileName || "").toLowerCase().match(/\.[^.]+$/);
  return match ? match[0] : "";
}

function isMuxVideoFile(fileName) {
  return [".mp4", ".avi", ".mkv", ".webm", ".mov"].includes(fileSuffix(fileName));
}

function isQueueVideoFile(fileName) {
  return [".mp4", ".avi", ".mkv", ".webm", ".mov"].includes(fileSuffix(fileName));
}

function isMuxAudioFile(fileName) {
  return [".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"].includes(fileSuffix(fileName));
}

function modeUsesMic() {
  return micSourceCheckbox.checked;
}

function modeUsesSystem() {
  return systemSourceCheckbox.checked;
}

function modeUsesScreen() {
  return screenSourceCheckbox.checked;
}

function modeUsesMouse() {
  return mouseSourceCheckbox.checked && modeUsesScreen();
}

function modeUsesKeyboard() {
  return keyboardSourceCheckbox.checked && modeUsesScreen();
}

function hasSelectableDevice(select) {
  return Array.from(select.options).some((option) => !option.disabled && option.value !== "");
}

function selectHasValue(select, value) {
  return Array.from(select.options).some((option) => option.value === String(value ?? ""));
}

function setRecordingUi(recording) {
  isRecording = recording;
  startRecordButton.disabled = recording || isTranscribing || queueActive || benchmarkActive || videoMuxInFlight || hasAddingInProgress();
  stopRecordButton.disabled = !recording;
  for (const checkbox of recordingSourceCheckboxes) {
    checkbox.disabled = recording;
  }
  micDeviceSelect.disabled = recording ? !modeUsesMic() || micSwitchInFlight : micSwitchInFlight;
  outputDeviceSelect.disabled = recording ? !modeUsesSystem() || outputSwitchInFlight : outputSwitchInFlight;
  refreshMicDevicesButton.disabled = micDevicesRefreshInFlight;
  refreshOutputDevicesButton.disabled = outputDevicesRefreshInFlight;
  screenFpsSelect.disabled = recording || !modeUsesScreen();
  for (const control of displayCardControls()) {
    control.disabled = recording || !modeUsesScreen();
  }
  syncInputSourceControls(recording);

  if (!isTranscribing) {
    setAppState(t(recording ? "recordingActive" : "readyToRecord"), recording ? "active" : "idle");
  }
  setVideoMuxUi();
}

function syncInputSourceControls(recording) {
  const screenEnabled = modeUsesScreen();
  if (!screenEnabled) {
    mouseSourceCheckbox.checked = false;
    keyboardSourceCheckbox.checked = false;
  }
  mouseSourceCheckbox.disabled = recording || !screenEnabled;
  keyboardSourceCheckbox.disabled = recording || !screenEnabled;
  for (const checkbox of [mouseSourceCheckbox, keyboardSourceCheckbox]) {
    checkbox.closest(".source-checkbox").dataset.disabled = String(!screenEnabled);
  }
  updateInputSourceHint();
}

function updateInputSourceHint() {
  if (!modeUsesScreen()) {
    inputSourceHint.textContent = t("inputSourcesScreenRequired");
    inputSourceHint.hidden = false;
    inputSourceHint.dataset.type = "info";
    return;
  }
  if (keyboardSourceCheckbox.checked) {
    inputSourceHint.textContent = t("keyboardPrivacyHint");
    inputSourceHint.hidden = false;
    inputSourceHint.dataset.type = "warning";
    return;
  }
  inputSourceHint.textContent = "";
  inputSourceHint.hidden = true;
  inputSourceHint.dataset.type = "info";
}

function setVideoMuxUi() {
  const blocked = videoMuxInFlight || isRecording || isTranscribing || queueActive || benchmarkActive || hasAddingInProgress();
  videoMuxVideoSelect.disabled = blocked;
  videoMuxMicSelect.disabled = blocked;
  videoMuxSystemSelect.disabled = blocked;
  videoMuxButton.disabled = blocked || !videoMuxVideoSelect.value;
}

async function requestJson(url, options = {}) {
  let response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    throw new ApiError(t("failedFetch"));
  }
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = translateUiText(payload?.detail?.message || payload?.message || t("requestError"));
    const technicalDetails = translateUiText(payload?.detail?.technical_details || payload?.technical_details || "");
    throw new ApiError(message, technicalDetails);
  }

  return payload;
}

function formatElapsed(totalSeconds) {
  const seconds = Math.max(0, Math.floor(Number(totalSeconds) || 0));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainder = seconds % 60;
  return [hours, minutes, remainder].map((value) => String(value).padStart(2, "0")).join(":");
}

function updateRecordingTimerUi() {
  if (recordingStartedAtMs !== null) {
    const elapsed = (Date.now() - recordingStartedAtMs) / 1000;
    recordingTimer.textContent = t("recordingNow", { value: formatElapsed(elapsed) });
    return;
  }

  recordingTimer.textContent = lastRecordingDurationSec === null
    ? t("latestRecording", { value: "--:--:--" })
    : t("latestRecording", { value: formatElapsed(lastRecordingDurationSec) });
}

function syncRecordingTimer(status) {
  if (status.recording) {
    const elapsed = Number(status.recording_elapsed_sec || 0);
    recordingStartedAtMs = Date.now() - elapsed * 1000;
  } else {
    recordingStartedAtMs = null;
    if (status.last_recording_duration_sec !== null && status.last_recording_duration_sec !== undefined) {
      lastRecordingDurationSec = Number(status.last_recording_duration_sec);
    }
  }
  updateRecordingTimerUi();
}

function updateLevel(level, target, kind) {
  const levelPercent = Math.max(0, Math.min(100, Number(level.level || 0)));
  target.fill.style.width = `${levelPercent}%`;
  target.rms.textContent = t("rmsValue", { value: Number(level.rms || 0).toFixed(6) });
  target.peak.textContent = t("peakValue", { value: Number(level.peak || 0).toFixed(6) });

  const message = formatLevelMessage(kind, level);
  const details = level.warning ? `${message}\n${level.warning}` : message;
  setOutput(target.warning, details, level.has_signal ? "success" : "warning");
}

function resetLevel(target, message, type = "warning") {
  target.fill.style.width = "0%";
  target.rms.textContent = t("rmsZero");
  target.peak.textContent = t("peakZero");
  setOutput(target.warning, message, type);
}

function formatLevelMessage(kind, level) {
  const prefix = t(level.recording ? "levelRecording" : "levelIdle");
  const state = t(kind === "mic"
    ? (level.has_signal ? "micSignalPresent" : "micSignalMissing")
    : (level.has_signal ? "systemSignalPresent" : "systemSignalMissing"));
  return `${prefix} ${state}`;
}

function micLevelTarget() {
  return {
    fill: micLevelMeterFill,
    rms: micRmsValue,
    peak: micPeakValue,
    warning: micLevelWarning,
  };
}

function systemLevelTarget() {
  return {
    fill: systemLevelMeterFill,
    rms: systemRmsValue,
    peak: systemPeakValue,
    warning: systemLevelWarning,
  };
}

function recordingUsesMicInput() {
  return isRecording && modeUsesMic();
}

function recordingUsesSystemAudio() {
  return isRecording && modeUsesSystem();
}

async function loadDevices() {
  await Promise.all([
    refreshMicDevices(false),
    refreshOutputDevices(false),
    refreshDisplays(false),
  ]);
}

async function refreshMicDevices(announce = true) {
  const previousMicValue = micDeviceSelect.value;
  const wasRecording = isRecording;
  micDevicesRefreshInFlight = true;
  setRecordingUi(isRecording);
  if (announce) {
    setOutput(recordingOutput, t("refreshingDevices"));
  }

  try {
    const inputResult = await requestJson("/api/audio/devices");
    latestMicDevicesResult = inputResult;
    fillMicDevices(inputResult, previousMicValue);
    if (!wasRecording) {
      activeMicDeviceValue = micDeviceSelect.value;
    }
    if (announce) {
      setOutput(recordingOutput, t("micDevicesUpdated"), "success");
    }
  } catch (error) {
    if (previousMicValue && selectHasValue(micDeviceSelect, previousMicValue)) {
      micDeviceSelect.value = previousMicValue;
    }
    setOutput(recordingOutput, `${t("refreshMicDevicesFailed")}\n${error.message}`, "error");
  } finally {
    micDevicesRefreshInFlight = false;
    setRecordingUi(isRecording);
    refreshMicLevel();
  }
}

async function refreshOutputDevices(announce = true) {
  const previousOutputValue = outputDeviceSelect.value;
  const wasRecording = isRecording;
  outputDevicesRefreshInFlight = true;
  setRecordingUi(isRecording);
  if (announce) {
    setOutput(recordingOutput, t("refreshingDevices"));
  }

  try {
    const outputResult = await requestJson("/api/audio/output-devices");
    latestOutputDevicesResult = outputResult;
    fillOutputDevices(outputResult, previousOutputValue);
    if (!wasRecording) {
      activeOutputDeviceValue = outputDeviceSelect.value;
    }
    if (announce) {
      setOutput(recordingOutput, t("outputDevicesUpdated"), "success");
    }
  } catch (error) {
    if (previousOutputValue && selectHasValue(outputDeviceSelect, previousOutputValue)) {
      outputDeviceSelect.value = previousOutputValue;
    }
    setOutput(recordingOutput, `${t("refreshOutputDevicesFailed")}\n${error.message}`, "error");
  } finally {
    outputDevicesRefreshInFlight = false;
    setRecordingUi(isRecording);
    refreshSystemLevel();
  }
}

async function refreshDisplays(announce = true) {
  const previousSelection = selectedDisplayIndices();
  displayRefreshInFlight = true;
  if (announce) {
    setOutput(screenOutput, t("refreshingDisplays"));
  }

  try {
    const displays = await requestJson("/api/displays");
    latestDisplays = Array.isArray(displays) ? displays : [];
    fillDisplays(displays, previousSelection);
    displaysLoaded = true;
    if (announce) {
      setOutput(screenOutput, t("displaysUpdated"), "success");
    }
  } catch (error) {
    displayFoundSummary.textContent = t("displayListFailed");
    setOutput(screenOutput, `${t("displayListFailed")}\n${error.message}`, "error");
  } finally {
    displayRefreshInFlight = false;
    setRecordingUi(isRecording);
  }
}

function fillMicDevices(result, previousValue) {
  micDeviceSelect.innerHTML = "";
  const devices = result.devices || [];
  if (!devices.length) {
    const option = document.createElement("option");
    option.value = "";
    option.disabled = true;
    option.selected = true;
    option.textContent = t("microphonesNotFound");
    micDeviceSelect.append(option);
    return;
  }

  for (const device of devices) {
    const option = document.createElement("option");
    option.value = String(device.id);
    const defaultText = device.is_default ? ` ${t("defaultSuffix")}` : "";
    option.textContent = `${device.name} [${device.input_channels} ch, ${device.default_samplerate} Hz]${defaultText}`;
    micDeviceSelect.append(option);
  }

  const defaultId = result.default_device_id;
  const values = Array.from(micDeviceSelect.options).map((option) => option.value);
  if (previousValue && values.includes(previousValue)) {
    micDeviceSelect.value = previousValue;
  } else if (defaultId !== null && values.includes(String(defaultId))) {
    micDeviceSelect.value = String(defaultId);
  }
}

function fillOutputDevices(result, previousValue) {
  outputDeviceSelect.innerHTML = "";
  const devices = result.devices || [];
  if (!devices.length) {
    const option = document.createElement("option");
    option.value = "";
    option.disabled = true;
    option.selected = true;
    option.textContent = t("outputDevicesNotFound");
    outputDeviceSelect.append(option);
    return;
  }

  for (const device of devices) {
    const option = document.createElement("option");
    option.value = String(device.id);
    const defaultText = device.is_default_output ? ` ${t("defaultSuffix")}` : "";
    option.textContent = `${device.name} [${device.channels} ch, ${device.default_samplerate} Hz, ${device.api_name}]${defaultText}`;
    outputDeviceSelect.append(option);
  }

  const defaultId = result.default_output_device_id;
  const values = Array.from(outputDeviceSelect.options).map((option) => option.value);
  if (previousValue && values.includes(previousValue)) {
    outputDeviceSelect.value = previousValue;
  } else if (defaultId !== null && values.includes(String(defaultId))) {
    outputDeviceSelect.value = String(defaultId);
  }
}

function fillDisplays(displays, previousSelection = []) {
  const normalizedDisplays = sortDisplaysForLayout(Array.isArray(displays) ? displays : []);
  const previous = new Set(previousSelection.map((value) => Number(value)));
  displayList.innerHTML = "";

  if (!normalizedDisplays.length) {
    displayFoundSummary.textContent = t("displaysNotFound");
    const item = document.createElement("p");
    item.className = "empty";
    item.textContent = t("displaysNotFound");
    displayList.append(item);
    return;
  }

  displayFoundSummary.textContent = normalizedDisplays.length === 1
    ? t("displayFound")
    : t("displaysFound", { count: normalizedDisplays.length });

  const hasPreviousSelection = previous.size > 0;
  for (const [position, display] of normalizedDisplays.entries()) {
    const displayIndex = Number(display.index);
    const isDefault = Boolean(display.is_primary) || position === 0;
    displayList.append(createDisplayCard(display, {
      checked: hasPreviousSelection ? previous.has(displayIndex) : isDefault,
    }));
  }
}

function sortDisplaysForLayout(displays) {
  return [...displays].sort((left, right) => {
    const leftTop = Number(left.top || 0);
    const rightTop = Number(right.top || 0);
    if (leftTop !== rightTop) {
      return leftTop - rightTop;
    }
    const leftPosition = Number(left.left || 0);
    const rightPosition = Number(right.left || 0);
    if (leftPosition !== rightPosition) {
      return leftPosition - rightPosition;
    }
    return Number(left.index || 0) - Number(right.index || 0);
  });
}

function createDisplayCard(display, options = {}) {
  const displayIndex = Number(display.index);
  const card = document.createElement("article");
  const headingLabel = document.createElement("label");
  const input = document.createElement("input");
  const title = document.createElement("strong");
  const details = document.createElement("dl");
  const previewControls = document.createElement("div");
  const previewLabel = document.createElement("label");
  const previewCheckbox = document.createElement("input");
  const previewLabelText = document.createElement("span");
  const refreshButton = document.createElement("button");
  const previewFrame = document.createElement("div");
  const previewImage = document.createElement("img");
  const previewStatus = document.createElement("small");

  card.className = "display-card";
  card.dataset.displayIndex = String(displayIndex);

  headingLabel.className = "display-card-title";
  input.type = "checkbox";
  input.name = "screenDisplay";
  input.value = String(displayIndex);
  input.checked = Boolean(options.checked);
  title.textContent = t("screenCardLabel", { index: displayIndex });
  headingLabel.append(input, title);

  details.className = "display-card-details";
  appendDisplayDetail(details, t("displayResolution"), t("displayResolutionValue", {
    width: display.width,
    height: display.height,
  }));
  appendDisplayDetail(details, t("displayCoordinates"), t("displayCoordinatesValue", {
    left: display.left,
    top: display.top,
  }));
  appendDisplayDetail(details, t("displayMonitorIndex"), String(displayIndex));

  previewControls.className = "display-preview-controls";
  previewCheckbox.type = "checkbox";
  previewCheckbox.name = "displayPreview";
  previewCheckbox.value = String(displayIndex);
  previewLabelText.textContent = t("showPreview");
  previewLabel.append(previewCheckbox, previewLabelText);
  refreshButton.type = "button";
  refreshButton.dataset.previewDisplay = String(displayIndex);
  refreshButton.textContent = t("refreshPreview");
  refreshButton.hidden = true;
  previewControls.append(previewLabel, refreshButton);

  previewFrame.className = "display-preview-frame";
  previewFrame.hidden = true;
  previewImage.alt = t("previewAlt", { index: displayIndex });
  previewImage.hidden = true;
  previewStatus.textContent = t("previewOffByDefault");
  previewFrame.append(previewImage, previewStatus);

  previewCheckbox.addEventListener("change", async () => {
    previewLabelText.textContent = previewCheckbox.checked ? t("hidePreview") : t("showPreview");
    refreshButton.hidden = !previewCheckbox.checked;
    previewFrame.hidden = !previewCheckbox.checked;
    if (!previewCheckbox.checked) {
      previewImage.hidden = true;
      previewImage.removeAttribute("src");
      previewStatus.textContent = t("previewOffByDefault");
      return;
    }
    await refreshDisplayPreview(card);
  });
  refreshButton.addEventListener("click", () => refreshDisplayPreview(card));

  card.append(headingLabel, details, previewControls, previewFrame);
  return card;
}

function appendDisplayDetail(details, labelText, valueText) {
  const term = document.createElement("dt");
  const value = document.createElement("dd");
  term.textContent = labelText;
  value.textContent = valueText;
  details.append(term, value);
}

async function refreshDisplayPreview(card) {
  const displayIndex = Number(card.dataset.displayIndex);
  const image = card.querySelector("img");
  const status = card.querySelector("small");
  const button = card.querySelector("button[data-preview-display]");
  if (!Number.isInteger(displayIndex) || displayIndex < 1) {
    return;
  }
  button.disabled = true;
  status.textContent = t("previewLoading");
  image.hidden = true;
  try {
    const preview = await requestJson("/api/displays/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ screen_index: displayIndex, max_width: 340 }),
    });
    image.src = preview.image_data_url || `data:${preview.mime_type || "image/jpeg"};base64,${preview.image_base64}`;
    image.hidden = false;
    status.textContent = t("previewRefreshed");
  } catch (error) {
    image.hidden = true;
    image.removeAttribute("src");
    status.textContent = `${t("previewUnavailable")}\n${error.message}`;
  } finally {
    button.disabled = isRecording || !modeUsesScreen();
  }
}

async function handleMicDeviceChange() {
  if (isRecording && modeUsesMic()) {
    await switchMicDevice();
    return;
  }

  activeMicDeviceValue = micDeviceSelect.value;
  refreshMicLevel();
}

async function handleOutputDeviceChange() {
  if (isRecording && modeUsesSystem()) {
    await switchOutputDevice();
    return;
  }

  activeOutputDeviceValue = outputDeviceSelect.value;
  refreshSystemLevel();
}

async function switchMicDevice() {
  if (micSwitchInFlight) {
    return;
  }

  const previousValue = activeMicDeviceValue;
  const nextValue = micDeviceSelect.value;
  micSwitchInFlight = true;
  setRecordingUi(true);

  try {
    const result = await requestJson("/api/record/switch-microphone", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        device_id: nextValue === "" ? null : Number(nextValue),
      }),
    });
    activeMicDeviceValue = result.device_id === null || result.device_id === undefined
      ? ""
      : String(result.device_id);
    if (selectHasValue(micDeviceSelect, activeMicDeviceValue)) {
      micDeviceSelect.value = activeMicDeviceValue;
    }
    setOutput(recordingOutput, t("microphoneSwitched"), "success");
    showToast(t("microphoneSwitched"), "success");
    refreshMicLevel();
  } catch (error) {
    activeMicDeviceValue = previousValue;
    if (selectHasValue(micDeviceSelect, previousValue)) {
      micDeviceSelect.value = previousValue;
    }
    setOutput(recordingOutput, `${t("microphoneSwitchFailed")}\n${error.message}`, "error");
    showToast(t("microphoneSwitchFailed"), "error");
    refreshMicLevel();
  } finally {
    micSwitchInFlight = false;
    setRecordingUi(isRecording);
  }
}

async function switchOutputDevice() {
  if (outputSwitchInFlight) {
    return;
  }

  const previousValue = activeOutputDeviceValue;
  const nextValue = outputDeviceSelect.value;
  outputSwitchInFlight = true;
  setRecordingUi(true);

  try {
    const result = await requestJson("/api/record/switch-output-device", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        output_device_id: nextValue === "" ? null : nextValue,
      }),
    });
    activeOutputDeviceValue = result.output_device_id === null || result.output_device_id === undefined
      ? ""
      : String(result.output_device_id);
    if (selectHasValue(outputDeviceSelect, activeOutputDeviceValue)) {
      outputDeviceSelect.value = activeOutputDeviceValue;
    }
    setOutput(recordingOutput, t("outputDeviceSwitched"), "success");
    showToast(t("outputDeviceSwitched"), "success");
    refreshSystemLevel();
  } catch (error) {
    activeOutputDeviceValue = previousValue;
    if (selectHasValue(outputDeviceSelect, previousValue)) {
      outputDeviceSelect.value = previousValue;
    }
    setOutput(recordingOutput, `${t("outputDeviceSwitchFailed")}\n${error.message}`, "error");
    showToast(t("outputDeviceSwitchFailed"), "error");
    refreshSystemLevel();
  } finally {
    outputSwitchInFlight = false;
    setRecordingUi(isRecording);
  }
}

function updateModeUi() {
  micDeviceRow.dataset.active = String(modeUsesMic());
  systemDeviceRow.dataset.active = String(modeUsesSystem());
  micLevelBlock.dataset.active = String(modeUsesMic());
  systemLevelBlock.dataset.active = String(modeUsesSystem());
  screenControls.hidden = !modeUsesScreen();
  setRecordingUi(isRecording);
}

async function refreshStatus() {
  try {
    const status = await requestJson("/api/status");
    const transcription = status.transcription || {};
    const model = transcription.active_model || transcription.loaded_model || selectedModel() || status.whisper_model;
    latestTranscriptionStatus = transcription;
    transcriptionPhase = transcription.phase || null;
    activeRuntimeModel = model;

    if (!whisperModelSelect.dataset.initialized && status.whisper_models?.includes(status.whisper_model)) {
      whisperModelSelect.value = status.whisper_model;
      whisperModelSelect.dataset.initialized = "true";
    }
    if (status.whisper_model_status) {
      applyModelStatuses(status.whisper_model_status);
    }
    deviceAvailabilityOutput.textContent = transcription.cuda_available ? t("cpuGpu") : t("cpuOnly");

    syncRecordingTimer(status);
    isTranscribing = localTranscriptionActive || Boolean(transcription.in_progress);
    renderRuntimeDetails();
    if (status.recording && status.recording_mode) {
      setSourcesFromMode(status.recording_mode);
      screenSourceCheckbox.checked = Boolean(status.screen_recording?.is_recording);
      const eventLogging = status.screen_recording?.event_logging || {};
      mouseSourceCheckbox.checked = Boolean(eventLogging.mouse_enabled);
      keyboardSourceCheckbox.checked = Boolean(eventLogging.keyboard_enabled);
      updateModeUi();
    }
    setRecordingUi(Boolean(status.recording));
    updateRecordingTranscribeActions(lastRecordings);

    if (isTranscribing && !queueActive && !benchmarkActive) {
      setAppState(t("transcriptionRunning"), "active");
      const downloading = transcription.phase === "loading_model" && !modelStatusByName.get(model)?.local;
      showOperation(
        "transcription",
        downloading ? t("modelDownloading", { model }) : t("transcribing"),
        downloading ? t("modelDownloadText") : `${model} · ${runtime}/${compute}\n${t("wait")}`,
      );
    } else {
      hideOperation("transcription");
    }

    const ffmpeg = status.ffmpeg_found ? t("ffmpegFound") : t("ffmpegMissing");
    systemStatus.textContent = `${availabilityText(status)}; ${ffmpeg}`;
  } catch (error) {
    systemStatus.textContent = translateUiText(error.message);
  }
}

function availabilityText(status) {
  const micAvailable = Boolean(status.microphone?.available);
  const systemAvailable = Boolean(status.system_audio?.available);

  if (micAvailable && systemAvailable) {
    return t("devicesBoth");
  }
  if (!micAvailable && systemAvailable) {
    return t("devicesSystem");
  }
  if (micAvailable && !systemAvailable) {
    return t("devicesMic");
  }
  return t("devicesNone");
}

async function refreshMicLevel() {
  if (micLevelPollInFlight) {
    return;
  }

  if (!recordingUsesMicInput()) {
    resetLevel(micLevelTarget(), t("micLevelInactive"), "info");
    return;
  }

  if (!hasSelectableDevice(micDeviceSelect)) {
    resetLevel(micLevelTarget(), t("micDeviceNotSelected"));
    return;
  }

  micLevelPollInFlight = true;
  try {
    const deviceId = selectedMicDeviceId();
    const query = deviceId === null ? "" : `?device_id=${encodeURIComponent(deviceId)}`;
    const level = await requestJson(`/api/audio/level${query}`);
    updateLevel(level, micLevelTarget(), "mic");
  } catch (error) {
    resetLevel(
      micLevelTarget(),
      `${t("micAccessError")}\n${error.message}`,
      "error",
    );
  } finally {
    micLevelPollInFlight = false;
  }
}

async function refreshSystemLevel() {
  if (systemLevelPollInFlight) {
    return;
  }

  if (!recordingUsesSystemAudio()) {
    resetLevel(systemLevelTarget(), t("systemLevelInactive"), "info");
    return;
  }

  if (!hasSelectableDevice(outputDeviceSelect)) {
    resetLevel(systemLevelTarget(), t("systemDeviceNotSelected"));
    return;
  }

  systemLevelPollInFlight = true;
  try {
    const deviceId = selectedOutputDeviceId();
    const query = deviceId === null ? "" : `?device_id=${encodeURIComponent(deviceId)}`;
    const level = await requestJson(`/api/audio/output-level${query}`);
    updateLevel(level, systemLevelTarget(), "system");
  } catch (error) {
    resetLevel(
      systemLevelTarget(),
      `${t("systemAccessError")}\n${error.message}`,
      "error",
    );
  } finally {
    systemLevelPollInFlight = false;
  }
}

function formatRecordingDiagnostics(diagnostics) {
  if (diagnostics.source_type === "screen") {
    return formatScreenDiagnostics(diagnostics);
  }

  const source = recordingSourceLabel(diagnostics.source_type);
  const device = diagnostics.source_type === "system"
    ? `${diagnostics.output_device_name} (${diagnostics.output_device_id ?? t("defaultSuffix")})`
    : `${diagnostics.device_name} (${diagnostics.device_id ?? t("defaultSuffix")})`;

  const lines = [
    `${source}`,
    t("recordingDiagnosticWav", { path: diagnostics.audio_file }),
    t("recordingDiagnosticJson", { path: diagnostics.diagnostic_file }),
    t("recordingDiagnosticDevice", { device }),
    t("recordingDiagnosticDuration", { value: diagnostics.duration_sec }),
    t("rmsValue", { value: Number(diagnostics.rms).toFixed(6) }),
    t("peakValue", { value: Number(diagnostics.peak).toFixed(6) }),
  ];

  if (diagnostics.warnings?.length) {
    lines.push(...diagnostics.warnings);
  }

  return lines.join("\n");
}

function formatScreenDiagnostics(diagnostics) {
  const lines = [
    t("screenRecordingStopped"),
    t("recordingsSavedTo", { path: diagnostics.recordings_dir || diagnostics.session_dir }),
    t("screenSessionJson", { path: diagnostics.session_json }),
    t("screenDiagnosticDuration", { value: diagnostics.duration_sec }),
    t("screenDiagnosticFps", { value: diagnostics.fps }),
  ];

  const videoPaths = diagnostics.video_paths || [];
  if (videoPaths.length) {
    lines.push(t("screenVideoFiles", { value: videoPaths.join("\n") }));
  }
  const eventFiles = diagnostics.events || {};
  if (eventFiles.mouse) {
    lines.push(t("mouseEventsFile", { path: eventFiles.mouse }));
  }
  if (eventFiles.keyboard) {
    lines.push(t("keyboardEventsFile", { path: eventFiles.keyboard }));
  }
  for (const screen of diagnostics.screens || []) {
    if (screen.requested_fps) {
      lines.push(t("screenTimingDiagnostic", {
        index: screen.screen_index,
        requested: screen.requested_fps,
        actual: Number(screen.actual_capture_fps || 0).toFixed(1),
        duplicated: Math.round(Number(screen.duplicate_ratio || 0) * 100),
      }));
    }
  }
  if ((diagnostics.screens || []).some((screen) => screen.timing_warning)) {
    lines.push(t("screenTimingWarning"));
  }
  if ((diagnostics.screens || []).some((screen) => screen.cursor_warning)) {
    lines.push(t("screenCursorWarning"));
  }
  lines.push(...formatInputEventLoggingWarnings(diagnostics.event_logging || {}));
  if (diagnostics.error) {
    lines.push(diagnostics.error);
  }
  return lines.join("\n");
}

function formatInputEventLoggingWarnings(eventLogging) {
  const lines = [];
  if (eventLogging.mouse_status === "failed") {
    lines.push(t("inputEventLoggingFailed", {
      source: t("mouseSource"),
      error: eventLogging.mouse_error || t("notAvailable"),
    }));
  }
  if (eventLogging.keyboard_status === "failed") {
    lines.push(t("inputEventLoggingFailed", {
      source: t("keyboardSource"),
      error: eventLogging.keyboard_error || t("notAvailable"),
    }));
  }
  return lines;
}

function formatAllDiagnostics(diagnosticsList, errors = []) {
  const chunks = diagnosticsList.map(formatRecordingDiagnostics);
  if (errors.length) {
    chunks.push(t("diagnosticErrors", { value: errors.join("; ") }));
  }
  return chunks.join("\n\n");
}

function recordingSourceLabel(sourceType) {
  if (sourceType === "system") {
    return t("systemAudio");
  }
  if (sourceType === "mic") {
    return t("microphone");
  }
  if (sourceType === "screen") {
    return t("screenSource");
  }
  return translateUiText(sourceType || t("localFile"));
}

function formatRecordingPaths(recordings) {
  return recordings.map((item) => {
    if (item.source_type === "screen") {
      return [
        `${recordingSourceLabel(item.source_type)}: ${item.session_dir}`,
        ...(item.video_paths || []),
        ...formatInputEventLoggingWarnings(item.event_logging || {}),
      ].join("\n");
    }
    return `${recordingSourceLabel(item.source_type)}: ${item.file_path}`;
  }).join("\n");
}

function formatBenchmark(benchmark, benchmarkPath) {
  const speed = benchmark.realtime_factor ? `${benchmark.realtime_factor}x realtime` : t("notAvailable");
  return [
    t("benchmarkTxt", { value: benchmark.transcript_file }),
    t("benchmarkJson", { value: benchmarkPath }),
    t("benchmarkModel", { value: benchmark.model }),
    t("benchmarkDevice", { value: benchmark.device }),
    t("benchmarkComputeType", { value: benchmark.compute_type }),
    t("benchmarkAudioDuration", { value: benchmark.audio_duration_sec ?? t("notAvailable") }),
    t("benchmarkProcessingTime", { value: benchmark.transcribe_time_sec }),
    t("benchmarkSpeed", { value: speed }),
  ].join("\n");
}

function setRuntimeDetails({ model, device, compute, speed }, stateKey) {
  runtimeModel.textContent = model;
  runtimeDevice.textContent = device;
  runtimeCompute.textContent = compute;
  runtimeSpeed.textContent = speed;
  runtimeDetails.dataset.state = stateKey;
  runtimeDetails.setAttribute("aria-label", t(stateKey));
  runtimeDetails.title = t(stateKey);
}

function renderRuntimeDetails() {
  const transcription = latestTranscriptionStatus || {};
  const unavailable = t("notAvailable");

  if (queueActive) {
    const current = latestQueueStatus?.current_item;
    if (!current) {
      const notApplicable = t("statusNotApplicable");
      setRuntimeDetails({
        model: notApplicable,
        device: notApplicable,
        compute: notApplicable,
        speed: notApplicable,
      }, "statusNotApplicable");
      return;
    }
    const stage = latestQueueStatus.current_stage || current.stage;
    if (!audioRuntimeStages.has(stage)) {
      const notApplicable = t("statusNotApplicable");
      setRuntimeDetails({
        model: notApplicable,
        device: notApplicable,
        compute: notApplicable,
        speed: notApplicable,
      }, stage === "extracting_frames" ? "statusExtractingFrames" : stage === "ocr_processing" ? "statusOcrProcessing" : stage === "cv_processing" ? "statusCvProcessing" : "statusNotApplicable");
      return;
    }

    const audioPlan = processingPlanForQueueItem(current).audio;
    const runtimeMatchesItem = Boolean(
      transcription.in_progress
      && transcription.active_model === audioPlan.model
      && transcription.loaded_model === audioPlan.model,
    );
    setRuntimeDetails({
      model: audioPlan.model,
      device: runtimeMatchesItem ? (transcription.runtime_device || audioPlan.device) : audioPlan.device,
      compute: runtimeMatchesItem ? (transcription.runtime_compute_type || unavailable) : unavailable,
      speed: current.realtime_factor !== null && current.realtime_factor !== undefined
        ? `${current.realtime_factor}x`
        : unavailable,
    }, "statusTranscribingAudio");
    return;
  }

  const estimatingItem = latestQueueStatus?.items?.find((item) => item.estimate?.status === "estimating");
  if (estimatingItem || pendingRuntimeEstimateIds.size) {
    const estimating = t("estimating");
    setRuntimeDetails({
      model: estimating,
      device: estimating,
      compute: estimating,
      speed: estimating,
    }, "runtimeEstimate");
    return;
  }

  if (benchmarkActive && latestBenchmarkStatus?.current) {
    const current = latestBenchmarkStatus.current;
    setRuntimeDetails({
      model: current.model || transcription.active_model || unavailable,
      device: transcription.runtime_device || current.device || unavailable,
      compute: transcription.runtime_compute_type || unavailable,
      speed: unavailable,
    }, "statusTranscribingAudio");
    return;
  }

  if (latestQueueStatus && latestQueueStatus.status !== "empty" && !localTranscriptionActive) {
    const idle = t("statusIdle");
    setRuntimeDetails({ model: idle, device: idle, compute: idle, speed: idle }, "statusIdle");
    return;
  }

  if (isTranscribing) {
    setRuntimeDetails({
      model: transcription.active_model || transcription.loaded_model || unavailable,
      device: transcription.runtime_device || transcription.configured_device || unavailable,
      compute: transcription.runtime_compute_type || transcription.configured_compute_type || unavailable,
      speed: unavailable,
    }, "statusTranscribingAudio");
    return;
  }

  const idle = t("statusIdle");
  setRuntimeDetails({ model: idle, device: idle, compute: idle, speed: idle }, "statusIdle");
}

function updateRecordingTranscribeActions(recordings) {
  lastRecordings = recordings || [];
  const micRecording = lastRecordings.find((item) => item.source_type === "mic");
  const systemRecording = lastRecordings.find((item) => item.source_type === "system");
  const audioRecordings = lastRecordings.filter((item) => item.source_type === "mic" || item.source_type === "system");
  const blocked = isTranscribing || queueActive || benchmarkActive || hasAddingInProgress();
  recordingTranscribeActions.dataset.empty = String(lastRecordings.length === 0);
  transcribeMicRecordingButton.disabled = !micRecording || blocked;
  transcribeSystemRecordingButton.disabled = !systemRecording || blocked;
  transcribeAllRecordingsButton.disabled = audioRecordings.length < 2 || blocked;
}

async function addRecordingByType(sourceType) {
  const diagnostics = lastRecordings.find((item) => item.source_type === sourceType);
  if (!diagnostics) {
    setOutput(queueOutput, t("recordingFileNotFound"), "error");
    return;
  }
  await addRecordingsToQueue([diagnostics]);
}

async function addAllRecordings() {
  const audioRecordings = lastRecordings.filter((item) => item.source_type === "mic" || item.source_type === "system");
  if (audioRecordings.length < 2) {
    setOutput(queueOutput, t("twoRecordingsRequired"), "error");
    return;
  }
  await addRecordingsToQueue(audioRecordings);
}

async function addRecordingsToQueue(recordings) {
  const keys = recordings.map(recordingAddKey);
  if (isAddingRecording || hasPendingAddKey(keys)) {
    showAddStatus("queueRecordingAlreadyAdding", "warning");
    return;
  }
  if (recordings.some(activeQueueHasRecording)) {
    showAddStatus("queueFileAlreadyQueued", "warning");
    return;
  }
  const processingPlan = defaultProcessingPlanSnapshot();
  isAddingRecording = true;
  rememberPendingAdd(keys);
  showAddStatus("queueStageAddingFile");
  updateLongOperationControls();
  try {
    const status = await requestJson("/api/queue/add-recordings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        files: recordings.map((item) => ({
          file_path: item.audio_file,
          source_type: item.source_type,
        })),
        processing_plan: processingPlan,
        queue_folder_name: queueFolderNameValue(),
      }),
    });
    renderQueue(status);
    const message = t("recordingsAdded", { count: recordings.length });
    setOutput(queueOutput, message, "success");
    showToast(message, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  } finally {
    isAddingRecording = false;
    forgetPendingAdd(keys);
    restoreQueueStageStatus();
    updateLongOperationControls();
  }
}

async function addLocalFilesToQueue(files, input, pickerText, multiple = false) {
  if (!files.length) {
    setOutput(queueOutput, t(multiple ? "selectAtLeastOneFile" : "selectFile"), "error");
    return;
  }
  const keys = files.map(fileAddKey);
  if (isAddingFile || hasPendingAddKey(keys)) {
    showAddStatus("queueFileAlreadyAdding", "warning");
    return;
  }
  if (files.some(activeQueueHasFile)) {
    showAddStatus("queueFileAlreadyQueued", "warning");
    return;
  }
  const processingPlan = defaultProcessingPlanSnapshot();
  isAddingFile = true;
  rememberPendingAdd(keys);
  showAddStatus(addingFileLabelKey(files));
  updateLongOperationControls();
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  formData.append("processing_plan", JSON.stringify(processingPlan));
  formData.append("queue_folder_name", queueFolderNameValue());
  try {
    renderQueue(await requestJson("/api/queue/add-files", { method: "POST", body: formData }));
    resetFilePicker(input, pickerText, multiple);
    const message = t("filesAdded", { count: files.length });
    setOutput(queueOutput, message, "success");
    showToast(message, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  } finally {
    isAddingFile = false;
    forgetPendingAdd(keys);
    restoreQueueStageStatus();
    updateLongOperationControls();
  }
}

function transcriptFileName(value) {
  const text = String(value || "");
  return text.split(/[\\/]/).filter(Boolean).pop() || text;
}

function transcriptLoadSuccessMessage(filePath, announce) {
  const displayPath = displayOutputPath(filePath);
  if (announce) {
    return t("transcriptLoaded", { name: transcriptFileName(filePath), path: displayPath });
  }
  return `${t("latestTranscription")}: ${displayPath}`;
}

function queueItemTranscriptPath(item) {
  return item?.outputs?.transcript_path || item?.transcript_path || null;
}

function pathLooksLikeQueueTranscript(filePath) {
  const normalized = String(filePath || "").replaceAll("\\", "/").toLowerCase();
  return normalized.startsWith("data/queues/") || normalized.includes("/data/queues/");
}

async function loadTranscript(filePath, announce = false, reveal = false) {
  const requestedPath = String(filePath || "").trim();
  if (!requestedPath) {
    setOutput(transcriptPreviewOutput, t("transcriptReadFailed"), "error");
    return;
  }
  try {
    const result = await requestJson(`/api/transcripts/read?file_path=${encodeURIComponent(requestedPath)}`);
    const loadedPath = result.path || result.file_path || requestedPath;
    transcriptText.value = result.text || "";
    transcriptPathInput.value = loadedPath;
    lastLoadedTranscriptPath = loadedPath;
    setDynamicOutput(transcriptPreviewOutput, () => transcriptLoadSuccessMessage(loadedPath, announce), "success");
    if (reveal) {
      transcriptPreviewSection.open = true;
    }
  } catch (error) {
    setOutput(transcriptPreviewOutput, `${t("transcriptReadFailed")}: ${error.message}`, "error");
  }
}

function maybeLoadLatestQueueTranscript(status) {
  const terminalItems = [...(status.items || [])]
    .reverse()
    .filter((item) => terminalQueueStatuses.has(item.status) && queueItemTranscriptPath(item));
  const queueItem = terminalItems.find((item) => pathLooksLikeQueueTranscript(queueItemTranscriptPath(item)));
  const transcriptPath = queueItemTranscriptPath(queueItem || terminalItems[0]);
  if (transcriptPath && transcriptPath !== lastLoadedTranscriptPath) {
    loadTranscript(transcriptPath);
  }
}

async function maybeLoadLatestStorageTranscript(files) {
  if (lastLoadedTranscriptPath) {
    return;
  }
  const latestTranscript = (files || []).find((file) => file.name?.toLowerCase().endsWith(".txt"));
  const transcriptPath = latestTranscript?.path || latestTranscript?.name;
  if (transcriptPath) {
    await loadTranscript(transcriptPath);
  }
}

function showTechnicalDetails(details) {
  if (!details) {
    hideTechnicalDetails();
    return;
  }
  transcribeTechnicalText.textContent = details;
  transcribeTechnicalDetails.hidden = false;
}

function hideTechnicalDetails() {
  transcribeTechnicalText.textContent = "";
  transcribeTechnicalDetails.hidden = true;
  transcribeTechnicalDetails.open = false;
}

function storageFolderLabel(key) {
  return t({
    downloads: "storageDownloads",
    uploads: "storageUploads",
    recordings: "storageRecordings",
    transcripts: "storageTranscripts",
    logs: "storageLogs",
    jobs: "storageJobs",
  }[key] || "storageFolder");
}

function formatBytes(bytes) {
  const value = Number(bytes || 0);
  const units = ["B", "KB", "MB", "GB"];
  let size = Math.max(0, value);
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  const precision = unitIndex === 0 ? 0 : size >= 10 ? 1 : 2;
  return `${size.toFixed(precision)} ${units[unitIndex]}`;
}

function renderStorageSummary(summary) {
  storageSummaryGrid.innerHTML = "";
  const total = document.createElement("div");
  total.className = "storage-summary-card";
  total.append(
    textLine(t("storageTotalSize")),
    textLine(formatBytes(summary.total_size_bytes)),
  );
  storageSummaryGrid.append(total);
  for (const folder of summary.folders || []) {
    const card = document.createElement("div");
    card.className = "storage-summary-card";
    card.dataset.storageFolder = folder.key;
    card.append(
      textLine(storageFolderLabel(folder.key)),
      textLine(formatBytes(folder.size_bytes)),
    );
    const path = document.createElement("code");
    path.textContent = folder.path;
    card.append(path);
    storageSummaryGrid.append(card);
  }
}

async function refreshStorageSummary() {
  refreshStorageSummaryButton.disabled = true;
  try {
    const summary = await requestJson("/api/storage/summary");
    renderStorageSummary(summary);
  } catch (error) {
    setOutput(storageCleanupOutput, error.message, "error");
  } finally {
    refreshStorageSummaryButton.disabled = false;
  }
}

async function refreshStorageSettings() {
  try {
    const settings = await requestJson("/api/storage/settings");
    keepDownloadedMediaCheckbox.checked = Boolean(settings.keep_downloaded_url_media);
    keepUploadedTempCheckbox.checked = Boolean(settings.keep_uploaded_temp_files);
  } catch (error) {
    setOutput(storageCleanupOutput, error.message, "error");
  }
}

async function saveStorageSettings() {
  keepDownloadedMediaCheckbox.disabled = true;
  keepUploadedTempCheckbox.disabled = true;
  try {
    await requestJson("/api/storage/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        keep_downloaded_url_media: keepDownloadedMediaCheckbox.checked,
        keep_uploaded_temp_files: keepUploadedTempCheckbox.checked,
      }),
    });
    setLocalizedOutput(storageCleanupOutput, "storageSettingsSaved", {}, "success");
  } catch (error) {
    setOutput(storageCleanupOutput, error.message, "error");
    await refreshStorageSettings();
  } finally {
    keepDownloadedMediaCheckbox.disabled = false;
    keepUploadedTempCheckbox.disabled = false;
  }
}

function renderFrameSettings(settings) {
  latestFrameSettings = { ...latestFrameSettings, ...settings };
  defaultFrameMaxSizeSelect.value = latestFrameSettings.max_frame_size || "original";
}

async function refreshFrameSettings() {
  try {
    renderFrameSettings(await requestJson("/api/frames/settings"));
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
  }
}

async function saveFrameSettings() {
  try {
    renderFrameSettings(await requestJson("/api/frames/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ max_frame_size: defaultFrameMaxSizeSelect.value || "original" }),
    }));
    setLocalizedOutput(queueOutput, "frameSettingsSaved", {}, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    await refreshFrameSettings();
  }
}

function syncUrlDownloadCustomField() {
  urlDownloadCustomField.hidden = urlDownloadProfileSelect.value !== "custom";
}

function urlDownloadSettingsFromControls() {
  return {
    format_profile: urlDownloadProfileSelect.value || "auto",
    custom_format: urlDownloadCustomFormatInput.value.trim(),
    max_video_height: urlDownloadMaxVideoHeightSelect.value || "auto",
    log_media_probe: urlDownloadLogMediaProbe.checked,
    log_extraction_benchmark: urlDownloadLogExtractionBenchmark.checked,
  };
}

function renderUrlDownloadSettings(settings) {
  latestUrlDownloadSettings = { ...latestUrlDownloadSettings, ...settings };
  urlDownloadProfileSelect.value = latestUrlDownloadSettings.format_profile || "auto";
  urlDownloadCustomFormatInput.value = latestUrlDownloadSettings.custom_format || "";
  urlDownloadMaxVideoHeightSelect.value = latestUrlDownloadSettings.max_video_height || "auto";
  urlDownloadLogMediaProbe.checked = Boolean(latestUrlDownloadSettings.log_media_probe);
  urlDownloadLogExtractionBenchmark.checked = Boolean(latestUrlDownloadSettings.log_extraction_benchmark);
  syncUrlDownloadCustomField();
}

async function refreshUrlDownloadSettings() {
  try {
    renderUrlDownloadSettings(await requestJson("/api/url-download/settings"));
  } catch (error) {
    setOutput(urlDownloadSettingsOutput, error.message, "error");
  }
}

async function saveUrlDownloadSettings() {
  const requested = urlDownloadSettingsFromControls();
  const customFallback = requested.format_profile === "custom" && !requested.custom_format;
  urlDownloadSaveButton.disabled = true;
  try {
    const settings = await requestJson("/api/url-download/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requested),
    });
    renderUrlDownloadSettings(settings);
    const key = customFallback ? "urlDownloadCustomFallback" : "urlDownloadSettingsSaved";
    setLocalizedOutput(urlDownloadSettingsOutput, key, {}, customFallback ? "warning" : "success");
    showToast(t(key), customFallback ? "warning" : "success");
  } catch (error) {
    setOutput(urlDownloadSettingsOutput, error.message, "error");
  } finally {
    urlDownloadSaveButton.disabled = false;
  }
}

function ocrBackendTypeKey(type) {
  return {
    external_executable: "ocrTypeExternalExecutable",
    python_optional: "ocrTypeIntegratedOptional",
    python_optional_experimental: "ocrTypeOptionalExperimental",
    windows_system_experimental: "ocrTypeWindowsExperimental",
  }[type] || "ocrValueUnavailable";
}

function ocrBackendStatusKey(status) {
  return {
    available: "ocrStatusAvailable",
    not_found: "ocrStatusNotFound",
    not_installed: "ocrStatusNotInstalled",
    unsupported_platform: "ocrStatusUnsupportedPlatform",
    check_failed: "ocrStatusCheckFailed",
  }[status] || "ocrStatusCheckFailed";
}

function ocrBackendNoteKeys(backend) {
  if (backend.id === "easyocr" && backend.status === "not_installed") {
    return ["ocrEasyOcrMissing"];
  }
  if (backend.id === "windows_ocr") {
    const keys = ["ocrWindowsExperimentalNote"];
    if (backend.status === "unsupported_platform") {
      keys.push("ocrWindowsOnlyNote");
    } else if (backend.status === "not_installed") {
      keys.push("ocrOptionalDependenciesMissing");
    }
    return keys;
  }
  const keys = [];
  for (const note of backend.notes || []) {
    const key = {
      external_path_required: "ocrInstallHint",
      optional_dependency_missing: "ocrOptionalDependenciesMissing",
      experimental: "ocrExperimentalNote",
      windows_only: "ocrWindowsOnlyNote",
      import_check_failed: "ocrImportCheckFailed",
    }[note];
    if (key && !keys.includes(key)) {
      keys.push(key);
    }
  }
  return keys;
}

function easyOcrStatus(status = latestOcrStatus) {
  return status?.backends?.easyocr || {};
}

function easyOcrActionable(status = latestOcrStatus) {
  return Boolean(easyOcrStatus(status).available);
}

function renderOcrStatus(status) {
  latestOcrStatus = status;
  const backend = easyOcrStatus(status);
  const available = Boolean(backend.available);
  const warningStatuses = new Set(["not_found", "not_installed", "unsupported_platform"]);
  ocrStatusBadge.textContent = t(ocrBackendStatusKey(backend.status));
  ocrStatusBadge.dataset.status = available ? "success" : warningStatuses.has(backend.status) ? "warning" : "error";
  ocrBackendType.textContent = t(ocrBackendTypeKey(backend.type));
  ocrVersion.textContent = backend.version || t("ocrValueUnavailable");
  ocrLanguages.textContent = backend.languages?.length ? backend.languages.join(", ") : t("ocrLanguagesNone");
  ocrBackendNotes.textContent = ocrBackendNoteKeys(backend).map((key) => t(key)).join(" ");
  if (!easyOcrActionable(status)) {
    defaultOcrEnabled.checked = false;
  }
  updateLongOperationControls();
  if (available) {
    setLocalizedOutput(ocrStatusMessage, "ocrReadyForProcessing", {}, "success");
  } else if (warningStatuses.has(backend.status)) {
    setLocalizedOutput(ocrStatusMessage, "ocrEasyOcrUnavailable", {}, "warning");
  } else {
    setLocalizedOutput(
      ocrStatusMessage,
      "ocrImportCheckFailed",
      {},
      "error",
    );
  }
}

async function refreshOcrStatus() {
  try {
    renderOcrStatus(await requestJson("/api/ocr/status"));
  } catch (error) {
    setOutput(ocrStatusMessage, error.message, "error");
  }
}

async function checkOcrStatus() {
  ocrCheckButton.disabled = true;
  setLocalizedOutput(ocrStatusMessage, "ocrChecking");
  try {
    const status = await requestJson("/api/ocr/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        backend: "easyocr",
      }),
    });
    renderOcrStatus(status);
    showToast(t("ocrEnginesChecked"), "success");
  } catch (error) {
    setOutput(ocrStatusMessage, error.message, "error");
  } finally {
    ocrCheckButton.disabled = false;
  }
}

async function cleanupStorageFolder(folder) {
  const messageKey = folder === "downloads" ? "confirmClearDownloads" : "confirmClearUploads";
  if (!window.confirm(t(messageKey))) {
    return;
  }
  clearDownloadsButton.disabled = true;
  clearUploadsButton.disabled = true;
  try {
    const result = await requestJson("/api/storage/cleanup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder }),
    });
    if (result.errors?.length) {
      setOutput(storageCleanupOutput, t("cleanupPartial", { reason: result.errors.join("\n") }), "warning");
    } else {
      setOutput(storageCleanupOutput, t("cleanupCompleted"), "success");
    }
    await refreshStorage();
  } catch (error) {
    setOutput(storageCleanupOutput, t("cleanupFailed", { reason: error.message }), "error");
  } finally {
    clearDownloadsButton.disabled = false;
    clearUploadsButton.disabled = false;
  }
}

async function refreshStorage() {
  try {
    const storage = await requestJson("/api/storage");
    diskFree.textContent = t("diskFree", { value: storage.disk?.free_gb ?? "?" });
    recordingsPath.textContent = storage.recordings.path;
    transcriptsPath.textContent = storage.transcripts.path;
    latestRecordingFiles = storage.recordings.files || [];
    const transcriptFiles = storage.transcripts.files || [];
    renderFileList(recordingsFileList, latestRecordingFiles, t("recordingsEmpty"));
    renderFileList(transcriptsFileList, transcriptFiles, t("transcriptsEmpty"), true);
    await maybeLoadLatestStorageTranscript(transcriptFiles);
    fillVideoMuxOptions(latestRecordingFiles);
  } catch (error) {
    renderFileList(recordingsFileList, [], error.message);
    renderFileList(transcriptsFileList, [], error.message);
    latestRecordingFiles = [];
    fillVideoMuxOptions([]);
  }
  await refreshStorageSummary();
}

function fillVideoMuxOptions(files) {
  const previousVideo = videoMuxVideoSelect.value;
  const previousMic = videoMuxMicSelect.value;
  const previousSystem = videoMuxSystemSelect.value;
  const videoFiles = files.filter((file) => isMuxVideoFile(file.name));
  const audioFiles = files.filter((file) => isMuxAudioFile(file.name));

  fillSelectOptions(videoMuxVideoSelect, videoFiles, t("videoMuxNoVideo"), previousVideo, false);
  fillSelectOptions(videoMuxMicSelect, audioFiles, t("videoMuxNoMic"), previousMic, true);
  fillSelectOptions(videoMuxSystemSelect, audioFiles, t("videoMuxNoSystem"), previousSystem, true);
  setVideoMuxUi();
}

function fillSelectOptions(select, files, emptyLabel, previousValue, optional) {
  select.innerHTML = "";
  const emptyOption = document.createElement("option");
  emptyOption.value = "";
  emptyOption.textContent = emptyLabel;
  if (!optional && files.length) {
    emptyOption.disabled = true;
  }
  select.append(emptyOption);

  for (const file of files) {
    const option = document.createElement("option");
    option.value = file.name;
    option.textContent = file.name;
    select.append(option);
  }

  if (previousValue && Array.from(select.options).some((option) => option.value === previousValue)) {
    select.value = previousValue;
  } else if (!optional && files.length) {
    select.value = files[0].name;
  } else {
    select.value = "";
  }
}

function renderFileList(target, files, emptyMessage, clickableTranscripts = false) {
  target.innerHTML = "";

  if (!files.length) {
    const item = document.createElement("li");
    item.className = "empty";
    item.textContent = emptyMessage;
    target.append(item);
    return;
  }

  for (const file of files) {
    const item = document.createElement("li");
    const name = clickableTranscripts && file.name.toLowerCase().endsWith(".txt")
      ? document.createElement("button")
      : document.createElement("span");
    const meta = document.createElement("small");
    name.textContent = file.name;
    if (name instanceof HTMLButtonElement) {
      name.type = "button";
      name.className = "file-link";
      name.addEventListener("click", () => loadTranscript(file.path || file.name, true, true));
    }
    meta.textContent = `${formatDateTime(file.modified)} · ${file.size_mb} MB`;
    item.title = file.path;
    item.append(name, meta);
    target.append(item);
  }
}

function formatDateTime(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(window.LATI18N?.getLanguage() === "en" ? "en-US" : "ru-RU");
}

async function openFolder(folder) {
  try {
    const result = await requestJson("/api/folders/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder }),
    });
    showToast(result.message, "success");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function mergeVideoWithAudio() {
  const videoFile = videoMuxVideoSelect.value;
  const micAudioFile = videoMuxMicSelect.value;
  const systemAudioFile = videoMuxSystemSelect.value;
  if (!videoFile) {
    setOutput(videoMuxOutput, t("videoMuxSelectVideoError"), "error");
    return;
  }
  if (!micAudioFile && !systemAudioFile) {
    setOutput(videoMuxOutput, t("videoMuxSelectAudioError"), "error");
    return;
  }

  videoMuxInFlight = true;
  setVideoMuxUi();
  setOutput(videoMuxOutput, t("videoMuxStarted"), "info");

  try {
    const result = await requestJson("/api/video-mux/merge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        video_file: videoFile,
        mic_audio_file: micAudioFile || null,
        system_audio_file: systemAudioFile || null,
      }),
    });
    const message = t("videoMuxCompleted", { file: result.output_file || result.output_path });
    setOutput(videoMuxOutput, message, "success");
    showToast(message, "success");
    await refreshStorage();
  } catch (error) {
    setOutput(videoMuxOutput, `${t("videoMuxFailed")}\n${error.message}`, "error");
    showToast(t("videoMuxFailed"), "error");
  } finally {
    videoMuxInFlight = false;
    setVideoMuxUi();
  }
}

async function refreshModelStatuses() {
  try {
    const payload = await requestJson("/api/models");
    applyModelStatuses(payload.models || []);
    if (modelManagerStatus.textContent === t("modelManagerLoading")) {
      setModelManagerStatus(t("modelManagerReady"), "success");
    }
  } catch (error) {
    modelAvailabilityOutput.textContent = t("modelStatusError", { message: translateUiText(error.message) });
    modelDownloadWarning.textContent = "";
    modelDownloadWarning.dataset.type = "warning";
    setModelManagerStatus(t("modelStatusError", { message: translateUiText(error.message) }), "error");
    renderModelManager();
  }
}

function applyModelStatuses(statuses) {
  modelStatusByName = new Map(statuses.map((item) => [item.name, item]));
  populateModelSelect(whisperModelSelect, selectedModel());

  updateModelAvailabilityUi();
  renderModelManager();
}

function updateModelAvailabilityUi() {
  const status = modelStatusByName.get(selectedModel());
  if (!status) {
    modelAvailabilityOutput.textContent = t("modelChecking");
    modelDownloadWarning.textContent = "";
    modelDownloadWarning.dataset.type = "info";
    return;
  }

  modelAvailabilityOutput.textContent = `${status.name} - ${isModelDownloaded(status) ? t("modelLocal") : t("modelNotDownloaded")}. ${modelSizeLabel(status.name)}.`;

  if (isModelDownloaded(status)) {
    modelDownloadWarning.textContent = t("modelReady");
    modelDownloadWarning.dataset.type = "success";
    return;
  }

  const localizedHeavyWarning = status.name === "medium"
    ? t("mediumDownloadWarning")
    : status.name === "large-v3"
      ? t("largeDownloadWarning")
      : "";
  modelDownloadWarning.textContent = [
    t("modelNeedsDownload"),
    localizedHeavyWarning,
    localizedHeavyWarning ? t("downloadRequirementsWarning") : "",
  ].filter(Boolean).join("\n");
  modelDownloadWarning.dataset.type = status.name === "medium" || status.name === "large-v3" ? "warning" : "info";
  return;
}

function warnAboutSelectedModelDownload() {
  const status = modelStatusByName.get(selectedModel());
  if (status && !isModelDownloaded(status)) {
    showToast(t("modelDownloadFirstToast"), "warning");
  }
}

function modelKeyPrefix(model) {
  return {
    tiny: "Tiny",
    base: "Base",
    small: "Small",
    medium: "Medium",
    "large-v3": "LargeV3",
  }[model] || "Small";
}

function modelOptionDescription(model) {
  return t(`modelOption${modelKeyPrefix(model)}`);
}

function modelOptionLabel(model) {
  return `${model} - ${modelOptionDescription(model)}`;
}

function populateModelSelect(select, selectedValue) {
  select.innerHTML = "";
  for (const model of ["tiny", "base", "small", "medium", "large-v3"]) {
    const option = document.createElement("option");
    option.value = model;
    option.textContent = modelOptionLabel(model);
    option.selected = model === selectedValue;
    select.append(option);
  }
  if (!select.value) {
    select.value = "small";
  }
}

function modelSizeLabel(model) {
  return t(`modelSize${modelKeyPrefix(model)}`);
}

function modelInfoFieldKey(model, field) {
  return `modelInfo${modelKeyPrefix(model)}${field}`;
}

function isModelDownloaded(status) {
  return Boolean(status?.local || status?.is_downloaded || isModelReadyStatus(status?.status));
}

function isModelReadyStatus(statusCode) {
  return statusCode === "available" || statusCode === "ready";
}

function isModelFailedStatus(statusCode) {
  return statusCode === "download_error" || statusCode === "verification_error" || statusCode === "failed";
}

function normalizeModelStatus(statusCode) {
  if (isModelReadyStatus(statusCode)) {
    return "ready";
  }
  if (isModelFailedStatus(statusCode)) {
    return "failed";
  }
  return statusCode || "not_downloaded";
}

function displayedModelStatus(status) {
  const name = status?.name || "";
  if (deletingModels.has(name)) {
    return "deleting";
  }
  if (verifyingModels.has(name)) {
    return "verifying";
  }
  const overrideStatus = modelOperationStatusByName.get(name);
  if (overrideStatus) {
    return normalizeModelStatus(overrideStatus);
  }
  if (status?.status === "starting" || (modelDownloadStatus?.status === "starting" && modelDownloadStatus.model === name)) {
    return "starting";
  }
  if (status?.status === "downloading" || (modelDownloadStatus?.active && modelDownloadStatus.model === name)) {
    return "downloading";
  }
  if (isModelFailedStatus(status?.status)) {
    return "failed";
  }
  return isModelDownloaded(status) ? "ready" : "not_downloaded";
}

function modelStatusLabel(statusCode) {
  return {
    ready: t("modelStatusReady"),
    available: t("modelStatusAvailable"),
    starting: t("modelStatusStarting"),
    not_downloaded: t("modelStatusNotDownloaded"),
    downloading: t("modelStatusDownloading"),
    verifying: t("modelStatusVerifying"),
    failed: t("modelStatusFailed"),
    download_error: t("modelStatusDownloadError"),
    verification_error: t("modelStatusVerificationError"),
    deleting: t("modelStatusDeleting"),
  }[statusCode] || statusCode;
}

function setModelManagerStatus(message, type = "info") {
  modelManagerStatus.textContent = message;
  modelManagerStatus.dataset.type = type;
}

function createModelActionButton(labelKey, onClick, disabled = false, variant = "") {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = t(labelKey);
  button.disabled = disabled;
  if (variant) {
    button.dataset.variant = variant;
  }
  button.addEventListener("click", onClick);
  return button;
}

function renderModelManager() {
  if (!modelManagerBody) {
    return;
  }
  const statuses = Array.from(modelStatusByName.values());
  modelManagerBody.innerHTML = "";

  if (!statuses.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.textContent = t("modelManagerLoading");
    row.append(cell);
    modelManagerBody.append(row);
    return;
  }

  for (const status of statuses) {
    const row = document.createElement("tr");
    const name = document.createElement("td");
    const statusCell = document.createElement("td");
    const size = document.createElement("td");
    const actions = document.createElement("td");
    const statusCode = displayedModelStatus(status);
    const downloaded = isModelDownloaded(status);
    const busy = isTranscribing || queueActive || benchmarkActive || deletingModels.has(status.name) || verifyingModels.has(status.name);
    const downloadActive = Boolean(modelDownloadStatus?.active);

    name.textContent = status.name;
    statusCell.textContent = modelStatusLabel(statusCode);
    statusCell.dataset.status = statusCode;
    size.textContent = modelSizeLabel(status.name);
    actions.className = "model-manager-actions";

    if (!downloaded) {
      actions.append(createModelActionButton("downloadModel", () => downloadModel(status.name), busy || downloadActive));
    }
    actions.append(createModelActionButton("verifyModel", () => verifyModel(status.name), busy || downloadActive, "secondary"));
    if (downloaded || status.can_delete) {
      actions.append(createModelActionButton("deleteModel", () => deleteModel(status.name), busy || downloadActive, "danger"));
    }
    actions.append(createModelActionButton("modelInfo", () => showModelInfo(status.name), false, "secondary"));

    row.append(name, statusCell, size, actions);
    modelManagerBody.append(row);
  }
}

function clearModelDownloadProgressUi() {
  modelDownloadProgressBlock.hidden = true;
  modelDownloadProgress.removeAttribute("value");
  modelDownloadProgressText.textContent = t("modelManagerIdle");
  modelDownloadProgressNote.textContent = "";
}

function clearModelDownloadProgressForModel(model) {
  if (modelDownloadStatus?.active && modelDownloadStatus.model && modelDownloadStatus.model !== model) {
    return;
  }
  modelDownloadStatus = null;
  modelDownloadSeenActive = false;
  clearModelDownloadProgressUi();
}

function markModelReadyInUi(model) {
  const currentStatus = modelStatusByName.get(model);
  if (currentStatus) {
    modelStatusByName.set(model, {
      ...currentStatus,
      status: "available",
      local: true,
      is_downloaded: true,
    });
  }
  modelOperationStatusByName.delete(model);
  clearModelDownloadProgressForModel(model);
  updateModelAvailabilityUi();
  renderModelManager();
}

function renderModelDownloadStatus(status) {
  modelDownloadStatus = status || null;
  const active = Boolean(status?.active);
  if (active) {
    modelDownloadSeenActive = true;
    modelDownloadProgressBlock.hidden = false;
    modelDownloadProgressText.textContent = status.status === "starting"
      ? t("modelDownloadStarting")
      : t("modelDownloading", { model: status.model });
    if (Number.isFinite(Number(status.progress_percent))) {
      modelDownloadProgress.value = Number(status.progress_percent);
      modelDownloadProgressNote.textContent = t("modelProgressPercent", { value: Math.round(Number(status.progress_percent)) });
    } else {
      modelDownloadProgress.removeAttribute("value");
      modelDownloadProgressNote.textContent = t("modelProgressUnavailable");
    }
    setModelManagerStatus(
      status.status === "starting" ? t("modelDownloadStarting") : t("modelDownloadInProgress", { model: status.model }),
      "info",
    );
  } else if (status?.status === "download_error") {
    modelDownloadSeenActive = false;
    clearModelDownloadProgressUi();
    setModelManagerStatus(t("modelDownloadFailed"), "error");
  } else if (isModelReadyStatus(status?.status) && status.model) {
    modelDownloadSeenActive = false;
    clearModelDownloadProgressUi();
    setModelManagerStatus(t("modelDownloadCompleted", { model: status.model }), "success");
  } else if (status?.status === "verification_error") {
    modelDownloadSeenActive = false;
    clearModelDownloadProgressUi();
    setModelManagerStatus(t("modelVerifyFailed"), "error");
  } else if (!modelManagerStatus.textContent) {
    clearModelDownloadProgressUi();
    setModelManagerStatus(t("modelManagerReady"), "success");
  }
  renderModelManager();
}

async function refreshModelDownloadStatus(force = false) {
  if (!force && !modelDownloadSeenActive && !modelDownloadStatus?.active) {
    return;
  }
  const previousActive = Boolean(modelDownloadStatus?.active);
  try {
    const status = await requestJson("/api/models/download-status");
    renderModelDownloadStatus(status);
    if (previousActive && !status.active) {
      await refreshModelStatuses();
      if (status.status === "available") {
        showToast(t("modelDownloadCompleted", { model: status.model }), "success");
      } else if (status.status === "download_error") {
        showToast(t("modelDownloadFailed"), "error");
      }
    }
  } catch (error) {
    setModelManagerStatus(error.message, "error");
  }
}

async function downloadModel(model) {
  modelOperationStatusByName.set(model, "starting");
  renderModelDownloadStatus({
    active: true,
    model,
    status: "starting",
    progress_percent: null,
    progress_available: false,
    message: t("modelDownloadStarting"),
    error_message: null,
  });
  try {
    const status = await requestJson("/api/models/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model }),
    });
    renderModelDownloadStatus(status);
    if (status.accepted) {
      modelOperationStatusByName.delete(model);
      showToast(t("modelDownloadStarted", { model }), "info");
    } else {
      modelOperationStatusByName.delete(model);
      showToast(t("modelDownloadAlreadyRunning"), "warning");
    }
    await refreshModelStatuses();
  } catch (error) {
    modelOperationStatusByName.set(model, "download_error");
    renderModelDownloadStatus({
      active: false,
      model,
      status: "download_error",
      progress_percent: null,
      progress_available: false,
      message: t("modelDownloadFailed"),
      error_message: error.message,
    });
    showToast(t("modelDownloadFailed"), "error");
    renderModelManager();
  }
}

async function verifyModel(model) {
  verifyingModels.add(model);
  clearModelDownloadProgressForModel(model);
  modelOperationStatusByName.delete(model);
  setModelManagerStatus(t("modelVerifyInProgress", { model }), "info");
  renderModelManager();
  try {
    const result = await requestJson("/api/models/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, device: selectedDevice() }),
    });
    if (result.success) {
      modelOperationStatusByName.delete(model);
      const message = t("modelVerifySuccess", {
        model,
        device: result.resolved_device || selectedDevice(),
        compute: result.compute_type || "auto",
      });
      setModelManagerStatus(message, "success");
      showToast(message, "success");
      markModelReadyInUi(model);
    } else {
      clearModelDownloadProgressForModel(model);
      modelOperationStatusByName.set(model, result.status === "not_downloaded" ? "not_downloaded" : "verification_error");
      const message = result.status === "not_downloaded" ? t("modelVerifyNeedsDownload") : t("modelVerifyFailed");
      setModelManagerStatus(message, "error");
      showToast(message, "error");
    }
  } catch (error) {
    clearModelDownloadProgressForModel(model);
    modelOperationStatusByName.set(model, "verification_error");
    setModelManagerStatus(t("modelVerifyFailed"), "error");
    showToast(t("modelVerifyFailed"), "error");
  } finally {
    verifyingModels.delete(model);
    await refreshModelStatuses();
  }
}

async function deleteModel(model) {
  if (!window.confirm(t("modelDeleteConfirm", { model }))) {
    return;
  }
  deletingModels.add(model);
  modelOperationStatusByName.set(model, "deleting");
  setModelManagerStatus(t("modelDeleteInProgress", { model }), "info");
  renderModelManager();
  try {
    const result = await requestJson("/api/models/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, confirm: true }),
    });
    modelOperationStatusByName.delete(model);
    const message = result.deleted ? t("modelDeleteSuccess", { model }) : t("modelDeleteNothing", { model });
    setModelManagerStatus(message, result.deleted ? "success" : "warning");
    showToast(message, result.deleted ? "success" : "warning");
    if (activeInfoModel === model) {
      hideModelInfo();
    }
    await refreshModelStatuses();
  } catch (error) {
    modelOperationStatusByName.delete(model);
    setModelManagerStatus(t("modelDeleteFailed"), "error");
    showToast(t("modelDeleteFailed"), "error");
  } finally {
    deletingModels.delete(model);
    renderModelManager();
  }
}

async function showModelInfo(model) {
  activeInfoModel = model;
  try {
    await requestJson(`/api/models/info?model=${encodeURIComponent(model)}`);
  } catch (error) {
    setModelManagerStatus(error.message, "error");
    return;
  }
  modelInfoTitle.textContent = model;
  modelInfoList.innerHTML = "";
  const fields = [
    ["modelInfoOrigin", t("modelInfoOriginValue")],
    ["modelInfoParameters", t(modelInfoFieldKey(model, "Parameters"))],
    ["modelInfoSize", modelSizeLabel(model)],
    ["modelInfoPositioning", t(modelInfoFieldKey(model, "Positioning"))],
    ["modelInfoRecommendedUse", t(modelInfoFieldKey(model, "RecommendedUse"))],
    ["modelInfoHardware", t(modelInfoFieldKey(model, "Hardware"))],
  ];
  for (const [labelKey, value] of fields) {
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = t(labelKey);
    description.textContent = value;
    modelInfoList.append(term, description);
  }
  modelInfoPanel.hidden = false;
}

function hideModelInfo() {
  activeInfoModel = null;
  modelInfoPanel.hidden = true;
  modelInfoTitle.textContent = "";
  modelInfoList.innerHTML = "";
}

function queueStatusLabel(status) {
  return {
    pending: t("statusPending"),
    downloading: t("statusDownloading"),
    downloaded: t("statusDownloaded"),
    analyzing: t("statusAnalyzing"),
    extracting_audio: t("statusExtracting"),
    extracting_frames: t("statusExtractingFrames"),
    ocr_processing: t("statusOcrProcessing"),
    cv_processing: t("statusCvProcessing"),
    transcribing: t("statusTranscribing"),
    completed: t("statusCompleted"),
    error: t("statusError"),
    failed: t("statusError"),
    cancelled: t("statusCancelled"),
  }[status] || status;
}

function queueStageKey(stage) {
  return {
    idle: "queueStageIdle",
    adding_file: "queueStageAddingFile",
    adding_url: "queueStageAddingUrl",
    waiting_download: "queueStageWaitingDownload",
    preparing_source: "queueStagePreparingSource",
    downloading_media: "queueStageDownloadingMedia",
    downloading_video: "queueStageDownloadingVideo",
    cancelling_download: "queueStageCancellingDownload",
    download_cancelled: "queueStageDownloadCancelled",
    download_failed: "queueStageDownloadFailed",
    transcribing_audio: "queueStageTranscribingAudio",
    extracting_frames: "queueStageExtractingFrames",
    ocr_processing: "queueStageOcrProcessing",
    cv_processing: "queueStageCvProcessing",
    cancelling_transcription: "queueStageCancellingTranscription",
    cancelling: "queueStageCancelling",
    completed: "queueStageCompleted",
    failed: "queueStageFailed",
    cancelled: "queueStageCancelled",
    ocr_pending_future: "queueStageOcrFuture",
    cv_pending_future: "queueStageCvFuture",
    media_index_pending_future: "queueStageMediaIndexFuture",
  }[stage] || "queueStageIdle";
}

function queueStageFromStatus(status) {
  return {
    pending: "idle",
    downloading: "downloading_media",
    downloaded: "preparing_source",
    analyzing: "preparing_source",
    extracting_audio: "transcribing_audio",
    transcribing: "transcribing_audio",
    extracting_frames: "extracting_frames",
    ocr_processing: "ocr_processing",
    cv_processing: "cv_processing",
    completed: "completed",
    error: "failed",
    failed: "failed",
    cancelled: "cancelled",
  }[status] || "idle";
}

function queueStageLabel(queueItemOrStage) {
  if (typeof queueItemOrStage === "string") {
    return t(queueStageKey(queueItemOrStage));
  }
  const item = queueItemOrStage || {};
  const key = item.stage_label_key || queueStageKey(item.stage || queueStageFromStatus(item.status));
  return t(key);
}

function queueItemPosition(status, currentItem) {
  const index = currentItem?.index;
  if (!index || !Array.isArray(status.items)) {
    return null;
  }
  const position = status.items.findIndex((item) => item.index === index);
  return position >= 0 ? position + 1 : null;
}

function hasAddingInProgress() {
  return isAddingFile || isAddingUrl || isAddingRecording;
}

function formatQueueStageStatus(status) {
  const total = Number(status?.total_items || 0);
  const pending = Number(status?.pending_items || 0);
  const completed = Number(status?.completed_items || 0);
  const failed = Number(status?.failed_items || 0);
  const cancelled = Number(status?.cancelled_items || 0);
  const finished = completed + failed + cancelled;
  if (status?.status === "running") {
    const current = status.current_item || {};
    const stage = queueStageLabel(current);
    const item = status.current_file || current.stage_detail || current.source_filename || "-";
    const currentPosition = queueItemPosition(status, current) || Math.min(total, finished + 1) || 1;
    const percent = Number(current.stage_progress?.percent);
    if (current.stage_progress?.mode === "determinate" && Number.isFinite(percent)) {
      return t("queueStageStatusRunningProgress", {
        current: currentPosition,
        total,
        stage,
        item,
        value: Math.round(percent),
      });
    }
    return t("queueStageStatusRunning", { current: currentPosition, total, stage, item });
  }
  if (status?.status === "pending" && total) {
    return t("queueStageStatusPending", { pending, total, stage: queueStageLabel("idle") });
  }
  if (status?.status === "completed" && total) {
    return t("queueStageStatusComplete", { stage: queueStageLabel("completed") });
  }
  if (status?.status === "cancelled" && total) {
    return t("queueStageStatusComplete", { stage: queueStageLabel("cancelled") });
  }
  return t("queueStageStatusIdle");
}

function createQueueStageProgress(queueItem) {
  const progress = queueItem.stage_progress || {};
  if (!["determinate", "indeterminate"].includes(progress.mode)) {
    return null;
  }

  const isDownload = ["downloading_media", "downloading_video", "cancelling_download"].includes(queueItem.stage);
  const wrapper = document.createElement("div");
  wrapper.className = "queue-item-stage-progress";
  wrapper.dataset.progressMode = progress.mode;

  const label = document.createElement("div");
  label.className = "queue-item-stage-progress-label";
  label.textContent = t(isDownload ? "downloadProgress" : "stageProgress");
  const bar = document.createElement("progress");
  bar.max = 100;
  bar.setAttribute("aria-label", label.textContent);
  const percent = Number(progress.percent);
  if (progress.mode === "determinate" && Number.isFinite(percent)) {
    bar.value = Math.max(0, Math.min(100, percent));
  } else {
    bar.removeAttribute("value");
  }
  wrapper.append(label, bar);

  const details = document.createElement("div");
  details.className = "queue-item-stage-progress-details";
  if (progress.mode === "determinate" && Number.isFinite(percent)) {
    details.append(textLine(t("stageProgressPercent", { value: Math.round(percent) })));
  } else {
    details.append(textLine(t("working")), textLine(t("progressUnavailable")));
  }
  if (progress.downloaded_bytes !== null && progress.downloaded_bytes !== undefined) {
    details.append(textLine(t("downloadedAmount", { value: formatBytes(progress.downloaded_bytes) })));
  }
  if (progress.total_bytes !== null && progress.total_bytes !== undefined) {
    details.append(textLine(t("downloadSize", { value: formatBytes(progress.total_bytes) })));
  }
  if (progress.speed_bytes_per_sec !== null && progress.speed_bytes_per_sec !== undefined) {
    details.append(textLine(t("downloadSpeed", { value: formatBytes(progress.speed_bytes_per_sec) })));
  }
  if (progress.eta_sec !== null && progress.eta_sec !== undefined) {
    details.append(textLine(t("downloadEta", { value: formatReadableEstimateDuration(progress.eta_sec) })));
  }
  if (progress.completed_units !== null && progress.completed_units !== undefined) {
    details.append(textLine(t("stageProgressUnits", {
      completed: progress.completed_units,
      total: progress.total_units ?? t("notAvailable"),
    })));
  }
  wrapper.append(details);
  return wrapper;
}

function queueStageStatusType(status) {
  if (status?.status === "running") {
    return "info";
  }
  if (Number(status?.failed_items || 0) > 0) {
    return "warning";
  }
  if (status?.status === "completed") {
    return "success";
  }
  if (status?.status === "cancelled") {
    return "warning";
  }
  return "info";
}

function updateQueueStageStatus(status) {
  if (hasAddingInProgress()) {
    return;
  }
  setDynamicOutput(queueStageStatus, () => formatQueueStageStatus(status), queueStageStatusType(status));
}

function activeQueueItems() {
  return (latestQueueStatus?.items || []).filter((item) => !terminalQueueStatuses.has(item.status));
}

function normalizeQueueUrl(value) {
  const trimmed = String(value || "").trim();
  try {
    const url = new URL(trimmed);
    url.hash = "";
    url.protocol = url.protocol.toLowerCase();
    url.hostname = url.hostname.toLowerCase();
    return url.toString().replace(/\/(?=($|\?))/, "").toLowerCase();
  } catch (_error) {
    return trimmed.replace(/#.*$/, "").toLowerCase();
  }
}

function fileAddKey(file) {
  return `file:${file.name}:${file.size}:${file.lastModified}`;
}

function recordingAddKey(recording) {
  return `recording:${recording.source_type}:${recording.audio_file || ""}`;
}

function urlAddKey(url) {
  return `url:${normalizeQueueUrl(url)}`;
}

function hasPendingAddKey(keys) {
  return keys.some((key) => pendingAddKeys.has(key));
}

function rememberPendingAdd(keys) {
  for (const key of keys) {
    pendingAddKeys.add(key);
  }
}

function forgetPendingAdd(keys) {
  for (const key of keys) {
    pendingAddKeys.delete(key);
  }
}

function showAddStatus(labelKey, type = "info") {
  setDynamicOutput(queueStageStatus, () => t(labelKey), type);
  setDynamicOutput(queueOutput, () => t(labelKey), type);
}

function restoreQueueStageStatus() {
  if (latestQueueStatus) {
    updateQueueStageStatus(latestQueueStatus);
  } else {
    setDynamicOutput(queueStageStatus, () => t("queueStageStatusIdle"), "info");
  }
}

function activeQueueHasFile(file) {
  return activeQueueItems().some((item) => item.source_type !== "url" && item.source_filename === file.name);
}

function activeQueueHasRecording(recording) {
  const sourcePath = String(recording.audio_file || "").replaceAll("\\", "/").toLowerCase();
  return activeQueueItems().some((item) => {
    const itemPath = String(item.source_path || "").replaceAll("\\", "/").toLowerCase();
    return item.source_type === recording.source_type && itemPath === sourcePath;
  });
}

function activeQueueHasUrl(url) {
  const key = normalizeQueueUrl(url);
  return activeQueueItems().some((item) => item.source_type === "url" && normalizeQueueUrl(item.source_url) === key);
}

function addingFileLabelKey(files) {
  if (files.length === 1) {
    return isQueueVideoFile(files[0].name) ? "queueStageAddingVideoFile" : "queueStageAddingAudioFile";
  }
  return "queueStageAddingFile";
}

function queueFolderNameValue() {
  return queueFolderNameInput?.value.trim() || "";
}

function updateQueueFolderUi(status = null) {
  if (!queueFolderNameInput || !queueFolderPathOutput) {
    return;
  }
  queueFolderNameInput.disabled = queueActive || hasAddingInProgress() || Boolean(status?.queue_path);
  queueFolderPathOutput.textContent = status?.queue_path
    ? t("queueFolderPath", { path: displayOutputPath(status.queue_path) })
    : t("queueFolderPathPending");
}

function frameRateOptions() {
  return [
    { value: "interval:30", rate: { mode: "interval", seconds: 30 }, label: t("frameRateEvery30Seconds") },
    { value: "interval:20", rate: { mode: "interval", seconds: 20 }, label: t("frameRateEvery20Seconds") },
    { value: "interval:15", rate: { mode: "interval", seconds: 15 }, label: t("frameRateEvery15Seconds") },
    { value: "interval:10", rate: { mode: "interval", seconds: 10 }, label: t("frameRateEvery10Seconds") },
    { value: "interval:5", rate: { mode: "interval", seconds: 5 }, label: t("frameRateEvery5Seconds") },
    { value: "interval:3", rate: { mode: "interval", seconds: 3 }, label: t("frameRateEvery3Seconds") },
    { value: "interval:2", rate: { mode: "interval", seconds: 2 }, label: t("frameRateEvery2Seconds") },
    { value: "interval:1", rate: { mode: "interval", seconds: 1 }, label: t("frameRateEvery1Second") },
    { value: "fps:2", rate: { mode: "fps", fps: 2 }, label: t("frameRate2Fps") },
    { value: "fps:3", rate: { mode: "fps", fps: 3 }, label: t("frameRate3Fps") },
    { value: "fps:5", rate: { mode: "fps", fps: 5 }, label: t("frameRate5Fps") },
    { value: "fps:10", rate: { mode: "fps", fps: 10 }, label: t("frameRate10Fps") },
    { value: "fps:15", rate: { mode: "fps", fps: 15 }, label: t("frameRate15Fps") },
    { value: "fps:20", rate: { mode: "fps", fps: 20 }, label: t("frameRate20Fps") },
    { value: "fps:30", rate: { mode: "fps", fps: 30 }, label: t("frameRate30Fps") },
  ];
}

function frameMaxSizeOptions() {
  return [
    { value: "original", label: t("maxFrameSizeOriginal") },
    { value: "width_1920", label: t("maxFrameSizeWidth1920") },
    { value: "width_1280", label: t("maxFrameSizeWidth1280") },
    { value: "width_960", label: t("maxFrameSizeWidth960") },
    { value: "width_640", label: t("maxFrameSizeWidth640") },
  ];
}

function frameMaxSizeLabel(value) {
  return frameMaxSizeOptions().find((option) => option.value === value)?.label || t("maxFrameSizeOriginal");
}

function urlDownloadMaxVideoHeightLabel(value) {
  return {
    auto: t("urlDownloadMaxVideoHeightAuto"),
    480: t("urlDownloadMaxVideoHeight480"),
    720: t("urlDownloadMaxVideoHeight720"),
    1080: t("urlDownloadMaxVideoHeight1080"),
    1440: t("urlDownloadMaxVideoHeight1440"),
    2160: t("urlDownloadMaxVideoHeight2160"),
  }[String(value || "auto")] || t("urlDownloadMaxVideoHeightAuto");
}

function urlDownloadMaxVideoHeightOptions() {
  return ["auto", "480", "720", "1080", "1440", "2160"].map((value) => ({
    value,
    label: urlDownloadMaxVideoHeightLabel(value),
  }));
}

function frameRateValue(rate) {
  if (rate?.mode === "fps") {
    return `fps:${rate.fps || 10}`;
  }
  return `interval:${rate?.seconds || 10}`;
}

function frameRateFromValue(value) {
  const [mode, amount] = String(value || "interval:10").split(":");
  const numeric = Number(amount) || 10;
  return mode === "fps"
    ? { mode: "fps", fps: numeric }
    : { mode: "interval", seconds: numeric };
}

function populateDefaultProcessingControls() {
  populateModelSelect(whisperModelSelect, selectedModel());
  const previousRate = defaultFrameRateSelect.value || "interval:30";
  defaultFrameRateSelect.innerHTML = "";
  for (const optionSpec of frameRateOptions()) {
    const option = document.createElement("option");
    option.value = optionSpec.value;
    option.textContent = optionSpec.label;
    option.selected = optionSpec.value === previousRate;
    defaultFrameRateSelect.append(option);
  }
  if (![...defaultFrameRateSelect.options].some((option) => option.selected)) {
    defaultFrameRateSelect.value = "interval:30";
  }

  const previousQuality = defaultJpegQualitySelect.value || "75";
  defaultJpegQualitySelect.innerHTML = "";
  for (const value of [75, 80, 85, 90, 95, 100]) {
    const option = document.createElement("option");
    option.value = String(value);
    option.textContent = String(value);
    option.selected = String(value) === previousQuality;
    defaultJpegQualitySelect.append(option);
  }

  const previousMaxSize = defaultFrameMaxSizeSelect.value || latestFrameSettings.max_frame_size || "original";
  defaultFrameMaxSizeSelect.innerHTML = "";
  for (const optionSpec of frameMaxSizeOptions()) {
    const option = document.createElement("option");
    option.value = optionSpec.value;
    option.textContent = optionSpec.label;
    option.selected = optionSpec.value === previousMaxSize;
    defaultFrameMaxSizeSelect.append(option);
  }
  if (![...defaultFrameMaxSizeSelect.options].some((option) => option.selected)) {
    defaultFrameMaxSizeSelect.value = "original";
  }
}

function processingPlanFromValues({
  audioEnabled,
  model,
  device,
  framesEnabled,
  frameRate,
  jpegQuality,
  maxFrameSize,
  urlDownload,
  ocrEnabled,
  ocrBackend,
  ocrResolvedBackend,
  ocrLanguages,
  ocrEngineAvailable,
  cvMetadataEnabled,
}) {
  const selectedBackend = ocrBackend || "easyocr";
  const backend = selectedBackend === "auto"
    ? (ocrResolvedBackend || "easyocr")
    : selectedBackend;
  const backendStatus = latestOcrStatus?.backends?.[backend];
  const downloadSettings = urlDownload || latestUrlDownloadSettings;
  const backendAvailable = backendStatus
    ? Boolean(backendStatus.available)
    : Boolean(ocrEngineAvailable);
  const easyOcrReady = backend === "easyocr" && backendAvailable;
  const normalizedOcrEnabled = Boolean(ocrEnabled) && easyOcrReady;
  const normalizedFramesEnabled = Boolean(framesEnabled) || normalizedOcrEnabled;
  return {
    audio: {
      enabled: Boolean(audioEnabled),
      model: model || selectedModel(),
      device: device || selectedDevice(),
    },
    frames: {
      enabled: normalizedFramesEnabled,
      rate: frameRate,
      interval_sec: frameRate?.mode === "interval" ? frameRate.seconds : null,
      jpeg_quality: Number(jpegQuality || 75),
      max_frame_size: maxFrameSize || "original",
    },
    url_download: {
      format_profile: downloadSettings?.format_profile || "auto",
      custom_format: downloadSettings?.custom_format || "",
      max_video_height: downloadSettings?.max_video_height || "auto",
      log_media_probe: Boolean(downloadSettings?.log_media_probe ?? true),
      log_extraction_benchmark: Boolean(downloadSettings?.log_extraction_benchmark ?? true),
      status: "pending",
    },
    ocr: {
      enabled: normalizedOcrEnabled,
      requested_enabled: Boolean(ocrEnabled),
      backend: selectedBackend,
      resolved_backend: backend,
      engine: backend,
      languages: ocrLanguages || (backend === "tesseract" ? ["rus", "eng"] : ["ru", "en"]),
      status: normalizedOcrEnabled ? "pending" : Boolean(ocrEnabled) ? "unavailable" : "disabled",
      engine_available: backendAvailable,
    },
    cv: {
      enabled: Boolean(cvMetadataEnabled),
      metadata_enabled: Boolean(cvMetadataEnabled),
      object_detection_enabled: false,
      vlm_enabled: false,
      yolo_enabled: false,
      engine: "metadata",
      status: cvMetadataEnabled ? "pending" : "disabled",
    },
  };
}

function defaultProcessingPlanSnapshot() {
  return processingPlanFromValues({
    audioEnabled: defaultAudioEnabled.checked,
    model: selectedModel(),
    device: selectedDevice(),
    framesEnabled: defaultFramesEnabled.checked,
    frameRate: frameRateFromValue(defaultFrameRateSelect.value || "interval:30"),
    jpegQuality: defaultJpegQualitySelect.value || "75",
    maxFrameSize: defaultFrameMaxSizeSelect.value || latestFrameSettings.max_frame_size || "original",
    urlDownload: urlDownloadSettingsFromControls(),
    ocrEnabled: defaultOcrEnabled.checked && !defaultOcrEnabled.disabled,
    ocrBackend: "easyocr",
    ocrResolvedBackend: "easyocr",
    ocrEngineAvailable: easyOcrActionable(),
    cvMetadataEnabled: defaultCvMetadataEnabled.checked && !defaultCvMetadataEnabled.disabled,
  });
}

function processingPlanForQueueItem(queueItem) {
  const operations = queueItem.operations || {};
  const frameSettings = queueItem.frame_extraction || {};
  const plan = queueItem.processing_plan || {};
  const audio = plan.audio || {};
  const frames = plan.frames || {};
  const cv = plan.cv || {};
  return processingPlanFromValues({
    audioEnabled: audio.enabled ?? operations.transcribe_audio ?? true,
    model: audio.model || selectedModel(),
    device: audio.device || selectedDevice(),
    framesEnabled: frames.enabled ?? operations.extract_frames ?? false,
    frameRate: frames.rate || frameSettings.rate || frameRateFromValue("interval:10"),
    jpegQuality: frames.jpeg_quality || frameSettings.jpeg_quality || 90,
    maxFrameSize: frames.max_frame_size || frameSettings.max_frame_size || "original",
    urlDownload: plan.url_download,
    ocrEnabled: plan.ocr?.enabled ?? operations.ocr ?? false,
    ocrBackend: plan.ocr?.backend || plan.ocr?.engine,
    ocrResolvedBackend: plan.ocr?.resolved_backend || plan.ocr?.engine,
    ocrLanguages: plan.ocr?.languages,
    ocrEngineAvailable: plan.ocr?.engine_available,
    cvMetadataEnabled: cv.metadata_enabled ?? cv.enabled ?? operations.cv ?? false,
  });
}

function deviceLabel(device) {
  return {
    auto: t("auto"),
    cpu: "CPU",
    cuda: "GPU / CUDA",
  }[device] || device || t("auto");
}

function frameRateLabel(rate) {
  const value = frameRateValue(rate);
  return frameRateOptions().find((option) => option.value === value)?.label || value;
}

function urlDownloadProfileLabel(profile) {
  const key = {
    auto: "urlDownloadProfileAuto",
    best_for_extraction: "urlDownloadProfileBestForExtraction",
    best_quality: "urlDownloadProfileBestQuality",
    smallest_file: "urlDownloadProfileSmallestFile",
    prefer_webm: "urlDownloadProfilePreferWebm",
    prefer_mp4: "urlDownloadProfilePreferMp4",
    prefer_mkv: "urlDownloadProfilePreferMkv",
    prefer_mov: "urlDownloadProfilePreferMov",
    prefer_avi: "urlDownloadProfilePreferAvi",
    audio_friendly: "urlDownloadProfileAudioFriendly",
    custom: "urlDownloadProfileCustom",
  }[profile] || "urlDownloadProfileAuto";
  return t(key);
}

function createPlanSelect(values, selectedValue, datasetName, labeler = (value) => value) {
  const select = document.createElement("select");
  select.dataset[datasetName] = "true";
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labeler(value);
    option.selected = value === selectedValue;
    select.append(option);
  }
  return select;
}

function queueItemIsVideo(queueItem) {
  return queueItem.media_kind === "video"
    || queueItem.media_kind === "url"
    || queueItem.source_type === "url"
    || isQueueVideoFile(queueItem.source_filename || queueItem.source_path);
}

function formatDurationShort(seconds) {
  if (seconds === null || seconds === undefined) {
    return "";
  }
  return formatElapsed(seconds);
}

function formatQueueMediaSummary(queueItem) {
  if (!queueItemIsVideo(queueItem)) {
    return t("audio");
  }
  const metadata = queueItem.video_metadata || {};
  const dimensions = metadata.width && metadata.height ? `${metadata.width}x${metadata.height}` : "";
  const duration = formatDurationShort(metadata.duration_sec ?? queueItem.audio_duration_sec);
  return [queueItem.source_type === "url" ? t("urlMedia") : t("video"), dimensions, duration].filter(Boolean).join(" - ");
}

function formatDiskUsageEstimate(estimate) {
  if (!estimate?.min_bytes || !estimate?.max_bytes) {
    return t("frameDiskUsageNote");
  }
  const minMb = Math.max(1, Math.round(Number(estimate.min_bytes) / (1024 * 1024)));
  const maxMb = Math.max(minMb, Math.round(Number(estimate.max_bytes) / (1024 * 1024)));
  return t("frameDiskUsageRange", { min: minMb, max: maxMb });
}

function createQueueCheckbox(key, checked, disabled, name) {
  const label = document.createElement("label");
  label.className = "queue-option";
  const input = document.createElement("input");
  input.type = "checkbox";
  input.checked = Boolean(checked);
  input.disabled = disabled;
  input.dataset.queueOperation = name;
  const span = document.createElement("span");
  span.textContent = t(key);
  label.append(input, span);
  return label;
}

function createComingSoonOption(key) {
  const label = document.createElement("label");
  label.className = "queue-option queue-option-disabled";
  const input = document.createElement("input");
  input.type = "checkbox";
  input.disabled = true;
  const span = document.createElement("span");
  span.textContent = `${t(key)} ${t("comingSoon")}`;
  label.append(input, span);
  return label;
}

function createDisabledQueueOption(key) {
  const label = document.createElement("label");
  label.className = "queue-option queue-option-disabled";
  const input = document.createElement("input");
  input.type = "checkbox";
  input.disabled = true;
  const span = document.createElement("span");
  span.textContent = t(key);
  label.append(input, span);
  return label;
}

function createProcessingPlanSummary(queueItem) {
  const plan = processingPlanForQueueItem(queueItem);
  const wrapper = document.createElement("div");
  wrapper.className = "queue-processing-plan-summary";
  const heading = document.createElement("h4");
  heading.textContent = t("processingPlan");
  wrapper.append(heading);
  wrapper.append(
    textLine(t("processingPlanAudio", {
      value: plan.audio.enabled ? `${plan.audio.model} / ${deviceLabel(plan.audio.device)}` : t("disabled"),
    })),
    textLine(t("processingPlanFrames", {
      value: plan.frames.enabled
        ? `${frameRateLabel(plan.frames.rate)} / JPEG ${plan.frames.jpeg_quality}% / ${frameMaxSizeLabel(plan.frames.max_frame_size)}`
        : t("disabled"),
    })),
    textLine(t("processingPlanOcr", {
      value: plan.ocr.enabled
        ? `${t("ocrEasyOcrOption")} / ${(plan.ocr.languages || []).join(", ")}`
        : plan.ocr.status === "unavailable" ? t("ocrEasyOcrUnavailableShort") : t("disabled"),
    })),
    textLine(t("processingPlanCv", { value: plan.cv.metadata_enabled ? t("visualMetadata") : t("disabled") })),
  );
  if (queueItem.source_type === "url") {
    wrapper.append(textLine(t("processingPlanUrlDownload", {
      value: `${urlDownloadProfileLabel(plan.url_download.format_profile)} / ${urlDownloadMaxVideoHeightLabel(plan.url_download.max_video_height)}`,
    })));
  }
  return wrapper;
}

function runtimeEstimateActive(status = latestQueueStatus) {
  return pendingRuntimeEstimateIds.size > 0
    || Number(status?.estimating_items || 0) > 0
    || Boolean(status?.items?.some((item) => item.estimate?.status === "estimating"));
}

function runtimeEstimateDetailsKey(queueItem, status = latestQueueStatus) {
  return `${status?.job_id || "queue"}:${queueItem.index}:runtime-estimate-details`;
}

function formatReadableEstimateDuration(seconds) {
  if (seconds === null || seconds === undefined || !Number.isFinite(Number(seconds))) {
    return t("notAvailable");
  }
  const totalSeconds = Math.max(0, Math.round(Number(seconds)));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;
  if (hours) {
    return [
      t("durationHoursShort", { value: hours }),
      minutes ? t("durationMinutesShort", { value: minutes }) : "",
    ].filter(Boolean).join(" ");
  }
  if (minutes) {
    return [
      t("durationMinutesShort", { value: minutes }),
      remainingSeconds ? t("durationSecondsShort", { value: remainingSeconds }) : "",
    ].filter(Boolean).join(" ");
  }
  return t("durationSecondsShort", { value: remainingSeconds });
}

function approximateEstimateDuration(seconds) {
  return t("estimateAboutDuration", { duration: formatReadableEstimateDuration(seconds) });
}

function runtimeEstimateErrorMessage(estimate) {
  const key = {
    duration_unavailable: "estimateDurationUnavailable",
    url_download_required: "estimateUrlDownloadRequired",
    ffmpeg_unavailable: "estimateFfmpegUnavailable",
    sample_preparation_failed: "estimateSamplePreparationFailed",
    source_unavailable: "estimateSourceUnavailable",
  }[estimate?.error_code];
  return t(key || "estimateFailed");
}

function audioEstimateUnavailableMessage(audio) {
  const key = {
    no_audio_stream: "estimateAudioNoStream",
  }[audio?.reason] || "estimateAudioUnavailable";
  return t(key);
}

function ocrEstimateUnavailableMessage(ocr) {
  const key = {
    easyocr_unavailable: "estimateOcrUnavailableEasyOcr",
    ocr_backend_unsupported: "estimateOcrUnsupportedBackend",
    ocr_estimator_unconfigured: "estimateOcrUnavailableEstimator",
    ocr_sample_frames_unavailable: "estimateOcrUnavailableFrames",
    ocr_estimate_failed: "estimateOcrUnavailableFailed",
  }[ocr?.reason] || "estimateOcrUnavailable";
  return t(key);
}

function estimateBreakdownDuration(enabled, seconds) {
  return enabled ? approximateEstimateDuration(seconds) : t("disabled");
}

function createRuntimeEstimate(queueItem, status) {
  const estimate = queueItem.estimate;
  const wrapper = document.createElement("section");
  wrapper.className = "queue-runtime-estimate";
  wrapper.dataset.runtimeEstimateResult = "true";

  const heading = document.createElement("div");
  heading.className = "queue-runtime-estimate-heading";
  const title = document.createElement("h4");
  title.textContent = t("runtimeEstimate");
  heading.append(title);

  if (queueItem.status === "pending") {
    const button = document.createElement("button");
    const estimating = estimate?.status === "estimating" || pendingRuntimeEstimateIds.has(queueItem.index);
    button.type = "button";
    button.className = "queue-estimate-button";
    button.dataset.queueAction = "estimate";
    button.textContent = estimating ? t("estimating") : t("estimateTime");
    button.disabled = estimating || queueActive || runtimeEstimateActive(status);
    heading.append(button);
  }
  wrapper.append(heading);

  if (!estimate) {
    return wrapper;
  }
  if (estimate.status === "estimating") {
    const state = textLine(t("estimating"));
    state.dataset.type = "active";
    wrapper.append(state);
    return wrapper;
  }
  if (estimate.status === "failed") {
    const state = textLine(t("estimateFailed"));
    state.dataset.type = "error";
    wrapper.append(state, textLine(runtimeEstimateErrorMessage(estimate)));
    return wrapper;
  }

  const state = textLine(t("estimateComplete"));
  state.dataset.type = "success";
  wrapper.append(state);
  if (estimate.no_enabled_operations) {
    wrapper.append(textLine(t("noEnabledOperationsEstimate")));
    return wrapper;
  }

  const audio = estimate.audio || {};
  const frames = estimate.frames || {};
  const ocr = estimate.ocr || {};
  if (audio.enabled) {
    wrapper.append(textLine(audio.included_in_total === false
      ? t("estimateAudioUnavailableSummary")
      : t("estimateAudioSummary", {
        duration: approximateEstimateDuration(audio.estimated_full_runtime_sec),
      })));
  }
  if (frames.enabled) {
    wrapper.append(textLine(t("estimateFramesSummary", {
      duration: approximateEstimateDuration(frames.estimated_full_runtime_sec),
    })));
  }
  if (ocr.enabled) {
    wrapper.append(textLine(t(ocr.included_in_total ? "estimateOcrSummary" : "estimateOcrUnavailableSummary", {
      duration: approximateEstimateDuration(ocr.estimated_full_runtime_sec),
    })));
  }
  wrapper.append(textLine(t("totalEstimate", {
    duration: approximateEstimateDuration(estimate.total_estimated_full_runtime_sec),
  })));
  if (estimate.total_excludes_audio) {
    const warning = textLine(t("estimateAudioTotalExcluded"));
    warning.dataset.type = "warning";
    wrapper.append(warning);
  }
  if (estimate.total_excludes_ocr) {
    const warning = textLine(t("estimateOcrTotalExcluded"));
    warning.dataset.type = "warning";
    wrapper.append(warning);
  }

  const details = document.createElement("details");
  const detailsKey = runtimeEstimateDetailsKey(queueItem, status);
  details.dataset.runtimeEstimateDetailsKey = detailsKey;
  details.open = openRuntimeEstimateDetailsKeys.has(detailsKey);
  const summary = document.createElement("summary");
  summary.textContent = t("estimateDetails");
  details.append(
    summary,
    textLine(t("estimateBreakdownHeading")),
    textLine(audio.enabled && audio.included_in_total === false
      ? t("estimateAudioUnavailableBreakdown")
      : t("estimateTranscriptionBreakdown", {
        duration: estimateBreakdownDuration(audio.enabled, audio.estimated_full_runtime_sec),
      })),
    textLine(t("estimateFrameExtractionBreakdown", {
      duration: estimateBreakdownDuration(frames.enabled, frames.estimated_full_runtime_sec),
    })),
    textLine(t(ocr.enabled && !ocr.included_in_total ? "estimateOcrUnavailableBreakdown" : "estimateOcrBreakdown", {
      duration: estimateBreakdownDuration(ocr.enabled, ocr.estimated_full_runtime_sec),
    })),
    textLine(t("estimateTotalBreakdown", {
      duration: approximateEstimateDuration(estimate.total_estimated_full_runtime_sec),
    })),
    textLine(t("sampleSegment", {
    duration: formatReadableEstimateDuration(estimate.sample_duration_sec),
    })),
  );
  if (audio.enabled) {
    if (audio.included_in_total === false) {
      const unavailable = textLine(audioEstimateUnavailableMessage(audio));
      unavailable.dataset.type = "warning";
      details.append(unavailable, textLine(t("estimateAudioTotalExcluded")));
    } else {
      details.append(
        textLine(t("estimateAudioConfig", {
          model: audio.model,
          device: deviceLabel(audio.effective_device || audio.device),
        })),
        textLine(t("sampleRuntime", { duration: formatReadableEstimateDuration(audio.sample_runtime_sec) })),
        textLine(t("estimatedFullTime", { duration: approximateEstimateDuration(audio.estimated_full_runtime_sec) })),
        textLine(t("estimateSpeed", { value: Number(audio.speed_factor || 0).toFixed(1) })),
      );
    }
  }
  if (frames.enabled) {
    details.append(
      textLine(t("estimateFramesConfig", {
        rate: frameRateLabel(frames.rate),
        quality: frames.jpeg_quality,
        size: frameMaxSizeLabel(frames.max_frame_size),
      })),
      textLine(t("sampleFrames", { count: frames.sample_frames })),
      textLine(t("estimatedTotalFrames", { count: frames.estimated_total_frames })),
      textLine(t("sampleRuntime", { duration: formatReadableEstimateDuration(frames.sample_runtime_sec) })),
      textLine(t("estimatedFullTime", { duration: approximateEstimateDuration(frames.estimated_full_runtime_sec) })),
    );
  }
  if (ocr.enabled) {
    details.append(textLine(t("ocr")));
    if (ocr.included_in_total) {
      details.append(
        textLine(t("estimateOcrExpectedFrames", { count: ocr.expected_total_frames ?? t("notAvailable") })),
        textLine(t("estimateOcrSampledFrames", { count: ocr.sample_frames ?? 0 })),
        textLine(t("estimateOcrAveragePerFrame", {
          duration: approximateEstimateDuration(ocr.average_sec_per_frame),
        })),
        textLine(t("estimateOcrEngine", { engine: ocr.engine || "EasyOCR" })),
        textLine(t("estimateOcrFirstRunNote")),
      );
    } else {
      const unavailable = textLine(ocrEstimateUnavailableMessage(ocr));
      unavailable.dataset.type = "warning";
      details.append(
        unavailable,
        textLine(t("estimateOcrTotalExcluded")),
      );
    }
  }
  details.append(textLine(t("approximateEstimate")));
  wrapper.append(details);
  return wrapper;
}

function createAudioPlanSettings(queueItem, disabled) {
  const plan = processingPlanForQueueItem(queueItem);
  const wrapper = document.createElement("div");
  wrapper.className = "queue-audio-settings";

  const audioToggle = createQueueCheckbox("audio", plan.audio.enabled, disabled, "transcribe_audio");
  const modelLabel = document.createElement("label");
  modelLabel.className = "queue-setting-field";
  const modelText = document.createElement("span");
  modelText.textContent = t("model");
  const modelSelect = createPlanSelect(
    ["tiny", "base", "small", "medium", "large-v3"],
    plan.audio.model,
    "queueAudioModel",
    modelOptionLabel,
  );
  modelSelect.disabled = disabled || !plan.audio.enabled;
  modelLabel.append(modelText, modelSelect);

  const deviceLabelElement = document.createElement("label");
  deviceLabelElement.className = "queue-setting-field";
  const deviceText = document.createElement("span");
  deviceText.textContent = t("device");
  const deviceSelect = createPlanSelect(["auto", "cpu", "cuda"], plan.audio.device, "queueAudioDevice", deviceLabel);
  deviceSelect.disabled = disabled || !plan.audio.enabled;
  deviceLabelElement.append(deviceText, deviceSelect);

  wrapper.append(audioToggle, modelLabel, deviceLabelElement);
  return wrapper;
}

function createOcrPlanSettings(queueItem, disabled) {
  const plan = processingPlanForQueueItem(queueItem);
  const wrapper = document.createElement("div");
  wrapper.className = "queue-ocr-settings";
  const currentBackendStatus = latestOcrStatus?.backends?.easyocr;
  const backendAvailable = currentBackendStatus
    ? Boolean(currentBackendStatus.available)
    : Boolean(plan.ocr.engine_available);
  const actionable = queueItemIsVideo(queueItem) && backendAvailable;
  const ocrToggle = createQueueCheckbox(
    "ocrEasyOcrOption",
    plan.ocr.enabled,
    disabled || !actionable,
    "ocr",
  );
  if (!actionable) {
    ocrToggle.classList.add("queue-option-disabled");
  }
  const note = document.createElement("p");
  note.className = "section-note";
  note.textContent = actionable
    ? t("ocrRunsOnExtractedFrames")
    : t("ocrEasyOcrUnavailable");
  wrapper.append(
    ocrToggle,
    createDisabledQueueOption("ocrTesseractSoon"),
    createDisabledQueueOption("ocrPaddleSoon"),
    createDisabledQueueOption("ocrWindowsSoon"),
    note,
  );
  return wrapper;
}

function createCvPlanSettings(queueItem, disabled) {
  const plan = processingPlanForQueueItem(queueItem);
  const wrapper = document.createElement("div");
  wrapper.className = "queue-cv-settings";
  const actionable = queueItemIsVideo(queueItem);
  const metadataToggle = createQueueCheckbox(
    "visualMetadata",
    plan.cv.metadata_enabled,
    disabled || !actionable,
    "cv",
  );
  if (!actionable) {
    metadataToggle.classList.add("queue-option-disabled");
  }
  const note = document.createElement("p");
  note.className = "section-note";
  note.textContent = actionable ? t("cvMetadataRequiresFrames") : t("statusNotApplicable");
  wrapper.append(
    metadataToggle,
    createDisabledQueueOption("cvObjectDetectionSoon"),
    createDisabledQueueOption("cvVlmAnalysisSoon"),
    createDisabledQueueOption("cvYoloObjectDetectionSoon"),
    note,
  );
  return wrapper;
}

function createUrlDownloadSettings(queueItem, disabled) {
  const plan = processingPlanForQueueItem(queueItem);
  const wrapper = document.createElement("div");
  wrapper.className = "queue-url-settings";
  wrapper.hidden = queueItem.source_type !== "url" && queueItem.media_kind !== "url";

  const maxHeightLabel = document.createElement("label");
  maxHeightLabel.className = "queue-setting-field";
  const maxHeightText = document.createElement("span");
  maxHeightText.textContent = t("urlDownloadMaxVideoHeightLabel");
  const maxHeightSelect = document.createElement("select");
  maxHeightSelect.dataset.queueUrlMaxHeight = "true";
  maxHeightSelect.disabled = disabled;
  const selectedMaxHeight = plan.url_download.max_video_height || "auto";
  for (const optionSpec of urlDownloadMaxVideoHeightOptions()) {
    const option = document.createElement("option");
    option.value = optionSpec.value;
    option.textContent = optionSpec.label;
    option.selected = optionSpec.value === selectedMaxHeight;
    maxHeightSelect.append(option);
  }
  maxHeightLabel.append(maxHeightText, maxHeightSelect);
  wrapper.append(maxHeightLabel);
  return wrapper;
}

function createFrameSettings(queueItem, disabled) {
  const settings = queueItem.frame_extraction || {};
  const operations = queueItem.operations || {};
  const wrapper = document.createElement("div");
  wrapper.className = "queue-frame-settings";
  wrapper.hidden = !operations.extract_frames;

  const rateLabel = document.createElement("label");
  rateLabel.className = "queue-setting-field";
  const rateText = document.createElement("span");
  rateText.textContent = t("frameExtractionRate");
  const rateSelect = document.createElement("select");
  rateSelect.dataset.queueFrameRate = "true";
  rateSelect.disabled = disabled || !operations.extract_frames;
  const selectedRate = frameRateValue(settings.rate);
  for (const optionSpec of frameRateOptions()) {
    const option = document.createElement("option");
    option.value = optionSpec.value;
    option.textContent = optionSpec.label;
    option.selected = optionSpec.value === selectedRate;
    rateSelect.append(option);
  }
  rateLabel.append(rateText, rateSelect);

  const qualityLabel = document.createElement("label");
  qualityLabel.className = "queue-setting-field";
  const qualityText = document.createElement("span");
  qualityText.textContent = t("jpegQuality");
  const qualitySelect = document.createElement("select");
  qualitySelect.dataset.queueJpegQuality = "true";
  qualitySelect.disabled = disabled || !operations.extract_frames;
  for (const value of [75, 80, 85, 90, 95, 100]) {
    const option = document.createElement("option");
    option.value = String(value);
    option.textContent = String(value);
    option.selected = Number(settings.jpeg_quality || 90) === value;
    qualitySelect.append(option);
  }
  qualityLabel.append(qualityText, qualitySelect);

  const maxSizeLabel = document.createElement("label");
  maxSizeLabel.className = "queue-setting-field";
  const maxSizeText = document.createElement("span");
  maxSizeText.textContent = t("maxFrameSize");
  const maxSizeSelect = document.createElement("select");
  maxSizeSelect.dataset.queueFrameSize = "true";
  maxSizeSelect.disabled = disabled || !operations.extract_frames;
  const selectedMaxSize = settings.max_frame_size || "original";
  for (const optionSpec of frameMaxSizeOptions()) {
    const option = document.createElement("option");
    option.value = optionSpec.value;
    option.textContent = optionSpec.label;
    option.selected = optionSpec.value === selectedMaxSize;
    maxSizeSelect.append(option);
  }
  maxSizeLabel.append(maxSizeText, maxSizeSelect);

  const estimate = document.createElement("div");
  estimate.className = "queue-frame-estimate";
  const count = settings.estimated_frame_count;
  if (queueItem.source_type === "url" && !queueItem.source_path && !queueItem.video_metadata) {
    estimate.append(textLine(t("frameEstimateAfterDownload")));
  } else {
    estimate.append(
      textLine(t("estimatedFrames", { count: count ?? t("notAvailable") })),
      textLine(formatDiskUsageEstimate(settings.estimated_disk_usage)),
    );
  }
  if (settings.estimated_frames_warning) {
    const warning = textLine(t("frameCountWarning"));
    warning.dataset.type = Number(count || 0) > 5000 ? "strong-warning" : "warning";
    estimate.append(warning);
  }
  if (queueItem.video_metadata_error) {
    const metadataWarning = textLine(queueItem.video_metadata_error);
    metadataWarning.dataset.type = "warning";
    estimate.append(metadataWarning);
  }

  wrapper.append(rateLabel, qualityLabel, maxSizeLabel, estimate);
  return wrapper;
}

function textLine(value) {
  const line = document.createElement("p");
  line.textContent = translateUiText(value);
  return line;
}

function displayOutputPath(path) {
  const normalized = String(path || "").replaceAll("\\", "/");
  const dataIndex = normalized.toLowerCase().lastIndexOf("/data/");
  return dataIndex >= 0 ? normalized.slice(dataIndex + 1) : normalized;
}

function queueItemOutputLines(queueItem) {
  const lines = [];
  const result = queueItem.frame_extraction_result || queueItem.frame_extraction?.result;
  const operations = queueItem.operations || {};
  const downloadedMediaPath = queueItem.downloaded_media_path || queueItem.downloaded_video_path || queueItem.downloaded_audio_path;
  if (queueItem.source_type === "url" && operations.extract_frames && downloadedMediaPath) {
    lines.push(t("downloadedMediaResultPath", { path: displayOutputPath(downloadedMediaPath) }));
  }
  if (queueItem.transcript_path) {
    lines.push(t("transcriptResultPath", { path: displayOutputPath(queueItem.transcript_path) }));
  }
  const framesPath = result?.frames_path || queueItem.frames_path;
  if (framesPath) {
    lines.push(t("framesResultFolder", { path: displayOutputPath(framesPath) }));
    lines.push(t("framesResultCount", { count: result?.extracted_frame_count ?? queueItem.extracted_frame_count ?? 0 }));
    lines.push(t("framesResultIndex", {
      path: displayOutputPath(result?.frames_index_path || queueItem.frames_index_path || `${framesPath}/frames_index.json`),
    }));
  }
  return lines;
}

function artifactPathLine(labelKey, path, exists) {
  if (!path) {
    return null;
  }
  const displayPath = exists === false ? t("artifactPathMissing", { path }) : path;
  return t(labelKey, { path: displayPath });
}

function queueItemArtifactLines(queueItem) {
  const outputs = queueItem.outputs || {};
  const lines = [];
  const addLine = (line) => {
    if (line) {
      lines.push(line);
    }
  };

  addLine(artifactPathLine("queueFolderArtifactPath", outputs.queue_path, outputs.queue_exists));
  addLine(artifactPathLine("queueManifestArtifactPath", outputs.queue_manifest_path, outputs.queue_manifest_exists));
  addLine(artifactPathLine("queueItemFolderArtifactPath", outputs.item_path, outputs.item_exists));
  addLine(artifactPathLine("sourceManifestArtifactPath", outputs.source_manifest_path, outputs.source_manifest_exists));
  addLine(artifactPathLine(
    outputs.transcript_partial ? "partialTranscriptArtifactPath" : "transcriptArtifactPath",
    outputs.transcript_path,
    outputs.transcript_exists,
  ));
  addLine(artifactPathLine("diagnosticJsonArtifactPath", outputs.json_path, outputs.json_exists));
  addLine(artifactPathLine("framesArtifactPath", outputs.frames_dir, outputs.frames_dir_exists));
  addLine(artifactPathLine("framesIndexArtifactPath", outputs.frames_index_path, outputs.frames_index_exists));
  addLine(artifactPathLine("ocrJsonlArtifactPath", outputs.ocr_jsonl_path, outputs.ocr_jsonl_exists));
  addLine(artifactPathLine("ocrTxtArtifactPath", outputs.ocr_txt_path, outputs.ocr_txt_exists));
  addLine(artifactPathLine("cvJsonlArtifactPath", outputs.cv_jsonl_path, outputs.cv_jsonl_exists));
  addLine(artifactPathLine("cvTxtArtifactPath", outputs.cv_txt_path, outputs.cv_txt_exists));

  if (outputs.downloaded_media_deleted) {
    lines.push(t("downloadedMediaDeleted"));
  } else {
    addLine(artifactPathLine("downloadedMediaArtifactPath", outputs.downloaded_media_path, outputs.downloaded_media_exists));
  }
  if (outputs.uploaded_temp_deleted) {
    lines.push(t("uploadedTempDeleted"));
  } else {
    addLine(artifactPathLine("uploadedTempArtifactPath", outputs.uploaded_temp_path, outputs.uploaded_temp_exists));
  }
  if (outputs.downloaded_media_delete_error) {
    lines.push(t("artifactCleanupError", { reason: outputs.downloaded_media_delete_error }));
  }
  if (outputs.uploaded_temp_delete_error) {
    lines.push(t("artifactCleanupError", { reason: outputs.uploaded_temp_delete_error }));
  }
  if (outputs.retention_cleanup_error) {
    lines.push(t("artifactCleanupError", { reason: outputs.retention_cleanup_error }));
  }

  if (!lines.length) {
    lines.push(...queueItemOutputLines(queueItem));
  }
  if (!lines.length && terminalQueueStatuses.has(queueItem.status)) {
    lines.push(t("noFilesCreated"));
  }
  return lines;
}

function queueControlHasActiveFocus() {
  const activeElement = document.activeElement;
  return Boolean(activeElement && queueList.contains(activeElement) && activeElement.matches(queueControlSelector));
}

function formatQueueItemError(queueItem) {
  const frameResult = queueItem.frame_extraction_result || queueItem.frame_extraction?.result;
  if (frameResult?.error_code === "frame_write_failed") {
    return t("frameWriteError", {
      filename: frameResult.error_filename || frameResult.error_message?.replace("Could not write JPEG frame: ", "") || "-",
    });
  }
  if (queueItem.error_message?.startsWith("Could not write JPEG frame: ")) {
    return t("frameWriteError", { filename: queueItem.error_message.replace("Could not write JPEG frame: ", "") });
  }
  return translateUiText(queueItem.error_message || "");
}

function createQueueItemElement(queueItem, status) {
  const item = document.createElement("li");
  const itemPlan = processingPlanForQueueItem(queueItem);
  const itemOcrPlan = itemPlan.ocr;
  item.className = "queue-item-card";
  item.dataset.queueIndex = String(queueItem.index);
  item.dataset.mediaKind = queueItem.media_kind || (queueItemIsVideo(queueItem) ? "video" : "audio");
  item.dataset.queueStage = queueItem.stage || queueStageFromStatus(queueItem.status);
  item.dataset.ocrLanguages = JSON.stringify(itemOcrPlan.languages);
  item.dataset.ocrEngineAvailable = String(itemOcrPlan.engine_available);
  item.dataset.urlDownload = JSON.stringify(itemPlan.url_download);

  const header = document.createElement("div");
  header.className = "queue-item-header";
  const titleBlock = document.createElement("div");
  titleBlock.className = "queue-item-title";
  const name = document.createElement("span");
  const sourceLabel = queueItem.source_type === "url"
    ? t("queueSourceUrl", {
      name: queueItem.source_title || queueItem.source_filename,
      platform: queueItem.source_platform || "unknown",
    })
    : t("queueSourceFile", {
      name: queueItem.source_filename,
      type: queueItem.source_type === "mic"
        ? t("microphone")
        : queueItem.source_type === "system"
          ? t("systemAudio")
          : t("localFile"),
    });
  name.textContent = `${queueItem.index}. ${sourceLabel}`;
  const mediaSummary = document.createElement("small");
  mediaSummary.textContent = formatQueueMediaSummary(queueItem);
  titleBlock.append(name, mediaSummary);

  const headerActions = document.createElement("div");
  headerActions.className = "queue-item-actions";
  const state = document.createElement("small");
  state.textContent = queueStatusLabel(queueItem.status);
  state.dataset.type = queueItem.status;
  headerActions.append(state);

  const isCurrent = status.current_item?.index === queueItem.index;
  const canRemove = queueItem.status === "pending";
  const cancellationPending = Boolean(queueItem.cancel_requested)
    || pendingQueueCancellationIds.has(queueItem.index)
    || ["cancelling_download", "cancelling_transcription", "cancelling"].includes(queueItem.stage);
  const canCancelDownload = isCurrent && !cancellationPending && queueItem.status === "downloading";
  const canCancelTranscription = isCurrent
    && !cancellationPending
    && ["extracting_audio", "transcribing"].includes(queueItem.status);
  const canCancelFrameExtraction = isCurrent && !cancellationPending && queueItem.status === "extracting_frames";
  const canCancelOcr = isCurrent && !cancellationPending && queueItem.status === "ocr_processing";
  const canCancelCv = isCurrent && !cancellationPending && queueItem.status === "cv_processing";
  const canCancel = canCancelDownload || canCancelTranscription || canCancelFrameExtraction || canCancelOcr || canCancelCv;
  const currentButCannotCancel = isCurrent && !canCancel && status.status === "running";
  if (canRemove || canCancel || currentButCannotCancel) {
    const actionButton = document.createElement("button");
    actionButton.type = "button";
    actionButton.className = canCancel || currentButCannotCancel
      ? "queue-item-remove queue-item-cancel"
      : "queue-item-remove";
    actionButton.textContent = canRemove
      ? "\u00d7"
      : cancellationPending
        ? t(queueItem.stage === "cancelling_download" ? "cancellingDownload" : "cancelling")
      : canCancelDownload
        ? t("cancelDownload")
      : canCancelTranscription
        ? t("cancelTranscription")
        : t("cancelCurrentShort");
    actionButton.dataset.queueAction = canRemove ? "remove" : "cancel";
    actionButton.disabled = cancellationPending || currentButCannotCancel;
    actionButton.title = cancellationPending
      ? t(queueItem.stage === "cancelling_download" ? "cancellingDownload" : "cancelling")
      : canCancelDownload
        ? t("cancelDownload")
      : canCancelTranscription
      ? t("transcriptionCancelAfterSegment")
      : canCancelFrameExtraction
        ? t("cancelCurrentItem")
      : canCancelOcr
        ? t("cancelCurrentItem")
      : currentButCannotCancel
        ? t("runningItemCannotCancel")
        : t("removeFromQueue");
    actionButton.setAttribute("aria-label", actionButton.title);
    headerActions.append(actionButton);
  }

  header.append(titleBlock, headerActions);
  item.append(header);

  const stageBlock = document.createElement("div");
  stageBlock.className = "queue-item-stage";
  stageBlock.dataset.queueStatus = queueItem.status || "";
  stageBlock.dataset.queueStage = queueItem.stage || queueStageFromStatus(queueItem.status);
  stageBlock.append(
    textLine(t("queueItemStatusLine", { status: queueStatusLabel(queueItem.status) })),
    textLine(t("queueItemStageLine", { stage: queueStageLabel(queueItem) })),
  );
  const stageProgress = createQueueStageProgress(queueItem);
  if (stageProgress) {
    stageBlock.append(stageProgress);
  }
  item.append(stageBlock);

  const options = queueItem.operations || {};
  const controlsDisabled = queueActive || runtimeEstimateActive(status) || queueItem.status !== "pending";
  const optionGroup = document.createElement("details");
  optionGroup.className = "queue-options queue-options-collapsible";
  optionGroup.dataset.queueSettingsPanel = "true";
  optionGroup.open = !collapsedQueueSettingsItemIds.has(queueItem.index);
  const optionSummary = document.createElement("summary");
  optionSummary.className = "queue-options-summary settings-collapsible-summary";
  const label = document.createElement("div");
  label.className = "queue-options-label";
  label.textContent = t("itemProcessingSettings");
  optionSummary.append(label, createProcessingPlanSummary(queueItem));
  const optionControls = document.createElement("div");
  optionControls.className = "queue-options-controls";
  optionControls.append(
    createAudioPlanSettings(queueItem, controlsDisabled),
    createUrlDownloadSettings(queueItem, controlsDisabled),
  );
  if (queueItemIsVideo(queueItem)) {
    optionControls.append(
      createQueueCheckbox("extractFrames", options.extract_frames, controlsDisabled || Boolean(options.ocr), "extract_frames"),
      createFrameSettings(queueItem, controlsDisabled),
      createOcrPlanSettings(queueItem, controlsDisabled),
      createCvPlanSettings(queueItem, controlsDisabled),
    );
  } else {
    optionControls.append(createOcrPlanSettings(queueItem, true), createCvPlanSettings(queueItem, true));
  }
  optionControls.append(createRuntimeEstimate(queueItem, status));
  optionGroup.append(optionSummary, optionControls);
  item.append(optionGroup);

  const outputLines = queueItemArtifactLines(queueItem);
  if (outputLines.length && terminalQueueStatuses.has(queueItem.status)) {
    const resultBlock = document.createElement("div");
    resultBlock.className = "queue-frame-result queue-output-artifacts";
    const heading = document.createElement("h4");
    heading.textContent = t("outputArtifactsTitle");
    resultBlock.append(heading);
    resultBlock.append(...outputLines.map((line) => textLine(line)));
    item.append(resultBlock);
  }

  if (queueItem.error_message) {
    const error = document.createElement("p");
    error.className = "queue-item-error";
    error.textContent = formatQueueItemError(queueItem);
    item.append(error);
  }

  if (queueItem.technical_details) {
    const details = document.createElement("details");
    details.className = "queue-item-technical";
    const summary = document.createElement("summary");
    summary.textContent = t("technicalDetails");
    const pre = document.createElement("pre");
    pre.textContent = translateUiText(queueItem.technical_details);
    details.append(summary, pre);
    item.append(details);
  }

  item.title = formatQueueItemError(queueItem) || translateUiText(queueItem.source_url || queueItem.source_path || "");
  return item;
}

function renderQueue(status, options = {}) {
  latestQueueStatus = status;
  queueActive = status.status === "running";
  for (const index of pendingQueueCancellationIds) {
    const item = status.items?.find((candidate) => candidate.index === index);
    if (!item || terminalQueueStatuses.has(item.status)) {
      pendingQueueCancellationIds.delete(index);
    }
  }
  for (const index of pendingRuntimeEstimateIds) {
    const item = status.items?.find((candidate) => candidate.index === index);
    if (!item || ["complete", "failed"].includes(item.estimate?.status)) {
      pendingRuntimeEstimateIds.delete(index);
    }
  }
  const visibleQueueItemIds = new Set((status.items || []).map((item) => item.index));
  for (const index of collapsedQueueSettingsItemIds) {
    if (!visibleQueueItemIds.has(index)) {
      collapsedQueueSettingsItemIds.delete(index);
    }
  }
  const visibleEstimateDetailsKeys = new Set((status.items || []).map((item) => runtimeEstimateDetailsKey(item, status)));
  for (const key of openRuntimeEstimateDetailsKeys) {
    if (!visibleEstimateDetailsKeys.has(key)) {
      openRuntimeEstimateDetailsKeys.delete(key);
    }
  }
  const total = Number(status.total_items || 0);
  const completed = Number(status.completed_items || 0);
  const failed = Number(status.failed_items || 0);
  const cancelled = Number(status.cancelled_items || 0);
  const pending = Number(status.pending_items || 0);
  const progress = Number(status.progress_percent || 0);
  const finished = completed + failed + cancelled;

  queueTotal.textContent = String(total);
  queueCompleted.textContent = String(completed);
  queueFailed.textContent = String(failed);
  queueCancelled.textContent = String(cancelled);
  queuePending.textContent = String(pending);
  queueCurrent.textContent = status.current_file || t("none");
  queueElapsed.textContent = formatElapsed(status.elapsed_sec);
  queueEta.textContent = status.eta_sec === null || status.eta_sec === undefined
    ? (translateUiText(status.eta_message) || t("queueEtaWaiting"))
    : formatElapsed(status.eta_sec);
  queueProgress.value = progress;
  queueProgressText.textContent = t("queueProgress", { done: finished, total, value: Math.round(progress) });
  updateQueueStageStatus(status);
  updateQueueFolderUi(status);
  renderRuntimeDetails();

  const preserveQueueControls = options.preserveFocusedQueueControls
    && (queueControlsFocused || queueControlHasActiveFocus());
  if (!preserveQueueControls) {
    queueList.innerHTML = "";
    if (!status.items?.length) {
      const item = document.createElement("li");
      item.textContent = t("queueEmpty");
      queueList.append(item);
    } else {
      for (const queueItem of status.items) {
        queueList.append(createQueueItemElement(queueItem, status));
      }
    }
  }

  queueAddButton.disabled = queueActive || hasAddingInProgress();
  queueFileInput.disabled = queueActive || hasAddingInProgress();
  queueFilePickerButton.disabled = queueActive || hasAddingInProgress();
  queueUrlAddButton.disabled = queueActive || hasAddingInProgress();
  queueUrlInput.disabled = queueActive || hasAddingInProgress();
  queueStartButton.disabled = queueActive || hasAddingInProgress() || pending === 0;
  queueStopButton.disabled = !queueActive || Boolean(status.stop_after_current);
  queueClearButton.disabled = queueActive || total === 0;
  queueRetryButton.disabled = queueActive || failed === 0;
  whisperModelSelect.disabled = queueActive || !defaultAudioEnabled.checked;
  whisperDeviceSelect.disabled = queueActive || !defaultAudioEnabled.checked;
  defaultOcrEnabled.disabled = queueActive || !easyOcrActionable();
  if (defaultOcrEnabled.disabled) {
    defaultOcrEnabled.checked = false;
  }
  defaultCvMetadataEnabled.disabled = queueActive;
  if (defaultOcrEnabled.checked) {
    defaultFramesEnabled.checked = true;
  }
  transcribeButton.disabled = queueActive || isTranscribing || hasAddingInProgress();
  setRecordingUi(isRecording);
  updateRecordingTranscribeActions(lastRecordings);

  if (queueActive) {
    const current = status.current_item || {};
    const modelLoading = transcriptionPhase === "loading_model" && !modelStatusByName.get(activeRuntimeModel)?.local;
    showOperation(
      "queue",
      current.status === "downloading"
        ? queueStageLabel(current)
        : modelLoading
          ? t("modelDownloading", { model: activeRuntimeModel })
          : t("queueRunning"),
      modelLoading ? t("modelDownloadText") : t("queueOverlay", {
        done: finished,
        total,
        item: status.current_file || "-",
        stage: queueStageLabel(current),
      }),
    );
  } else {
    hideOperation("queue");
  }

  if (previousQueueStatus === "running" && status.status === "completed") {
    const renderMessage = () => t("queueCompletedSummary", { completed, failed, cancelled });
    const message = renderMessage();
    setDynamicOutput(queueOutput, renderMessage, failed ? "warning" : "success");
    showToast(message, failed ? "warning" : "success");
    refreshStorage();
  } else if (previousQueueStatus === "running" && status.status === "cancelled") {
    setDynamicOutput(queueOutput, () => t("queueStopped"), "warning");
    showToast(t("queueStopped"), "warning");
  }

  const latestTechnicalItem = [...(status.items || [])]
    .reverse()
    .find((item) => item.technical_details);
  if (latestTechnicalItem) {
    showTechnicalDetails(translateUiText(latestTechnicalItem.technical_details));
  } else {
    hideTechnicalDetails();
  }
  maybeLoadLatestQueueTranscript(status);
  previousQueueStatus = status.status;
  updateLongOperationControls();
}

async function refreshQueueStatus() {
  try {
    renderQueue(await requestJson("/api/queue/status"), { preserveFocusedQueueControls: true });
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
  }
}

async function postQueueAction(url, successMessage) {
  try {
    const status = await requestJson(url, { method: "POST" });
    renderQueue(status);
    if (successMessage) {
      setOutput(queueOutput, successMessage, "success");
      showToast(successMessage, "success");
    }
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  }
}

function queueCardFromTarget(target) {
  return target.closest(".queue-item-card");
}

function collectQueueItemPayload(card) {
  const operations = {
    transcribe_audio: card.querySelector('[data-queue-operation="transcribe_audio"]')?.checked ?? true,
    extract_frames: card.querySelector('[data-queue-operation="extract_frames"]')?.checked ?? false,
    ocr: card.querySelector('[data-queue-operation="ocr"]')?.checked ?? false,
    cv: card.querySelector('[data-queue-operation="cv"]')?.checked ?? false,
  };
  if (operations.ocr) {
    operations.extract_frames = true;
  }
  const modelSelect = card.querySelector("[data-queue-audio-model]");
  const deviceSelect = card.querySelector("[data-queue-audio-device]");
  const rateSelect = card.querySelector("[data-queue-frame-rate]");
  const qualitySelect = card.querySelector("[data-queue-jpeg-quality]");
  const maxSizeSelect = card.querySelector("[data-queue-frame-size]");
  const urlMaxHeightSelect = card.querySelector("[data-queue-url-max-height]");
  const frameRate = frameRateFromValue(rateSelect?.value);
  const jpegQuality = Number(qualitySelect?.value || 90);
  const maxFrameSize = maxSizeSelect?.value || "original";
  const urlDownloadPlan = JSON.parse(card.dataset.urlDownload || "null") || undefined;
  if (urlDownloadPlan && urlMaxHeightSelect) {
    urlDownloadPlan.max_video_height = urlMaxHeightSelect.value || "auto";
  }
  const selectedOcrBackend = "easyocr";
  const resolvedOcrBackendForPayload = "easyocr";
  const resolvedOcrStatus = latestOcrStatus?.backends?.easyocr;
  const ocrEngineAvailable = resolvedOcrStatus
    ? Boolean(resolvedOcrStatus.available)
    : card.dataset.ocrEngineAvailable === "true";
  const processingPlan = processingPlanFromValues({
    audioEnabled: operations.transcribe_audio,
    model: modelSelect?.value || selectedModel(),
    device: deviceSelect?.value || selectedDevice(),
    framesEnabled: operations.extract_frames,
    frameRate,
    jpegQuality,
    maxFrameSize,
    urlDownload: urlDownloadPlan,
    ocrEnabled: operations.ocr,
    ocrBackend: selectedOcrBackend,
    ocrResolvedBackend: resolvedOcrBackendForPayload,
    ocrLanguages: JSON.parse(card.dataset.ocrLanguages || "null") || undefined,
    ocrEngineAvailable,
    cvMetadataEnabled: operations.cv,
  });
  return {
    index: Number(card.dataset.queueIndex),
    operations,
    frame_extraction: {
      rate: frameRate,
      jpeg_quality: jpegQuality,
      max_frame_size: maxFrameSize,
    },
    processing_plan: processingPlan,
  };
}

async function updateQueueItemFromCard(card) {
  if (!card || queueActive || runtimeEstimateActive()) {
    return;
  }
  try {
    renderQueue(await requestJson("/api/queue/update-item", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectQueueItemPayload(card)),
    }));
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
    await refreshQueueStatus();
  }
}

async function runRuntimeEstimate(card) {
  if (!card) {
    return;
  }
  const index = Number(card.dataset.queueIndex);
  if (pendingRuntimeEstimateIds.has(index) || runtimeEstimateActive()) {
    return;
  }
  pendingRuntimeEstimateIds.add(index);
  const button = card.querySelector('[data-queue-action="estimate"]');
  if (button) {
    button.disabled = true;
    button.textContent = t("estimating");
  }
  setOutput(queueOutput, t("estimating"), "info");
  renderRuntimeDetails();
  updateLongOperationControls();

  try {
    const updated = await requestJson("/api/queue/update-item", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectQueueItemPayload(card)),
    });
    renderQueue(updated);
    const status = await requestJson("/api/queue/estimate-item", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index }),
    });
    renderQueue(status);
    const estimate = status.items?.find((item) => item.index === index)?.estimate;
    const key = estimate?.status === "failed" ? "estimateFailed" : "estimateComplete";
    const type = estimate?.status === "failed" ? "error" : "success";
    setOutput(queueOutput, t(key), type);
    showToast(t(key), type);
  } catch (error) {
    pendingRuntimeEstimateIds.delete(index);
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
    await refreshQueueStatus();
  } finally {
    updateLongOperationControls();
    renderRuntimeDetails();
  }
}

async function removeOrCancelQueueItem(card, action) {
  if (!card) {
    return;
  }
  const index = Number(card.dataset.queueIndex);
  const url = action === "cancel" ? "/api/queue/cancel-item" : "/api/queue/remove-item";
  if (action === "cancel") {
    if (pendingQueueCancellationIds.has(index)) {
      return;
    }
    pendingQueueCancellationIds.add(index);
    const button = card.querySelector('[data-queue-action="cancel"]');
    if (button) {
      button.disabled = true;
      button.textContent = t(
        ["downloading_media", "downloading_video", "cancelling_download"].includes(card.dataset.queueStage)
          ? "cancellingDownload"
          : "cancelling",
      );
    }
    setOutput(queueOutput, t("cancelRequestSent"), "warning");
  }
  try {
    renderQueue(await requestJson(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index }),
    }));
    const message = action === "cancel" ? t("cancelRequestSent") : t("queueItemRemoved");
    setOutput(queueOutput, message, action === "cancel" ? "warning" : "success");
    showToast(message, action === "cancel" ? "warning" : "success");
  } catch (error) {
    if (action === "cancel") {
      pendingQueueCancellationIds.delete(index);
      await refreshQueueStatus();
    }
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  }
}

function validateQueueStartOptions() {
  const invalid = (latestQueueStatus?.items || []).find((item) => {
    const operations = item.operations || {};
    return item.status === "pending"
      && (queueItemIsVideo(item) || item.media_kind === "audio")
      && !operations.transcribe_audio
      && !operations.extract_frames
      && !operations.ocr
      && !operations.cv;
  });
  if (!invalid) {
    return true;
  }
  const message = invalid.source_type === "url"
    ? t("selectAtLeastOneUrlOperation")
    : queueItemIsVideo(invalid)
      ? t("selectAtLeastOneVideoOperation")
      : t("selectAtLeastOneAudioOperation");
  setOutput(queueOutput, message, "error");
  showToast(message, "error");
  return false;
}

function updateLongOperationControls() {
  const active = isTranscribing
    || queueActive
    || runtimeEstimateActive()
    || benchmarkActive
    || videoMuxInFlight
    || hasAddingInProgress();
  const fileAddBlocked = active || isAddingFile;
  const urlAddBlocked = active || isAddingUrl;
  const queueFolderLocked = Boolean(latestQueueStatus?.queue_path);
  whisperModelSelect.disabled = active || !defaultAudioEnabled.checked;
  whisperDeviceSelect.disabled = active || !defaultAudioEnabled.checked;
  transcribeButton.disabled = fileAddBlocked;
  audioFileInput.disabled = fileAddBlocked;
  audioFilePickerButton.disabled = fileAddBlocked;
  queueAddButton.disabled = fileAddBlocked;
  queueFileInput.disabled = fileAddBlocked;
  queueFilePickerButton.disabled = fileAddBlocked;
  queueUrlAddButton.disabled = urlAddBlocked;
  queueUrlInput.disabled = urlAddBlocked;
  if (queueFolderNameInput) {
    queueFolderNameInput.disabled = active || queueFolderLocked;
  }
  defaultAudioEnabled.disabled = active;
  defaultOcrEnabled.disabled = active || !easyOcrActionable();
  if (defaultOcrEnabled.disabled) {
    defaultOcrEnabled.checked = false;
  }
  defaultCvMetadataEnabled.disabled = active;
  if (defaultOcrEnabled.checked) {
    defaultFramesEnabled.checked = true;
  }
  defaultFramesEnabled.disabled = active || defaultOcrEnabled.checked;
  defaultFrameRateSelect.disabled = active || !defaultFramesEnabled.checked;
  defaultJpegQualitySelect.disabled = active || !defaultFramesEnabled.checked;
  defaultFrameMaxSizeSelect.disabled = active || !defaultFramesEnabled.checked;
  queueStartButton.disabled = active || Number(latestQueueStatus?.pending_items || 0) === 0;
  queueClearButton.disabled = active || Number(latestQueueStatus?.total_items || 0) === 0;
  queueRetryButton.disabled = active || Number(latestQueueStatus?.failed_items || 0) === 0;
  benchmarkUploadButton.disabled = active;
  benchmarkFileInput.disabled = active;
  benchmarkFilePickerButton.disabled = active;
  for (const button of benchmarkButtons) {
    button.disabled = active || !benchmarkSourceId;
  }
  refreshModelsButton.disabled = active || Boolean(modelDownloadStatus?.active);
  setRecordingUi(isRecording);
  setVideoMuxUi();
  updateRecordingTranscribeActions(lastRecordings);
  renderModelManager();
}

function formatBenchmarkResult(result) {
  if (!result) {
    return t("noResults");
  }
  return [
    `${result.device?.toUpperCase()} / ${result.benchmark_mode}`,
    t("benchmarkTotalWallTime", { value: result.total_wall_time_sec ?? "-" }),
    t("benchmarkModelLoadTime", { value: result.model_load_time_sec ?? "-" }),
    t("benchmarkTranscriptionTime", { value: result.transcription_time_sec ?? "-" }),
    t("benchmarkSaveTime", { value: result.save_time_sec ?? "-" }),
    t("benchmarkAudioDuration", { value: result.audio_duration_sec ?? "-" }),
    t("benchmarkRealtimeFactorTotal", { value: result.realtime_factor_total ?? "-" }),
    t("benchmarkPureModelFactor", { value: result.realtime_factor_transcription_only ?? "-" }),
    t("benchmarkComputeType", { value: result.compute_type ?? "-" }),
    t("benchmarkTxt", { value: result.transcript_path ?? "-" }),
    t("benchmarkJson", { value: result.json_path ?? "-" }),
  ].join("\n");
}

function renderBenchmark(status) {
  latestBenchmarkStatus = status;
  benchmarkActive = Boolean(status.running);
  benchmarkCpuResult.textContent = formatBenchmarkResult(status.results?.cpu);
  benchmarkCudaResult.textContent = formatBenchmarkResult(status.results?.cuda);
  if (benchmarkActive) {
    const current = status.current || {};
    const modelLoading = transcriptionPhase === "loading_model" && !modelStatusByName.get(activeRuntimeModel)?.local;
    showOperation(
      "benchmark",
      modelLoading ? t("modelDownloading", { model: activeRuntimeModel }) : t("benchmarkRunning"),
      modelLoading ? t("modelDownloadText") : `${(current.device || "").toUpperCase()} / ${current.mode || ""}\n${current.model || ""}\n${t("wait")}`,
    );
    setOutput(benchmarkStatusOutput, t("benchmarkRunning"));
  } else {
    hideOperation("benchmark");
    if (status.last_error) {
      setOutput(benchmarkStatusOutput, status.last_error, "error");
    }
  }
  renderRuntimeDetails();
  updateLongOperationControls();
}

async function refreshBenchmarkStatus() {
  try {
    renderBenchmark(await requestJson("/api/benchmark/status"));
  } catch (error) {
    setOutput(benchmarkStatusOutput, error.message, "error");
  }
}

startRecordButton.addEventListener("click", async () => {
  const mode = currentMode();
  const usesScreen = modeUsesScreen();
  if (!mode && !usesScreen) {
    setRecordingUi(false);
    setAppState(t("readyToRecord"), "idle");
    setOutput(recordingOutput, t("selectRecordingSource"), "error");
    showToast(t("selectRecordingSource"), "error");
    return;
  }
  if (usesScreen && !selectedDisplayIndices().length) {
    setRecordingUi(false);
    setAppState(t("readyToRecord"), "idle");
    setOutput(recordingOutput, t("selectDisplayToRecord"), "error");
    showToast(t("selectDisplayToRecord"), "error");
    return;
  }

  setOutput(recordingOutput, t("startingRecording"));
  updateRecordingTranscribeActions([]);
  startRecordButton.disabled = true;

  try {
    const result = await requestJson("/api/record/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode: mode || "none",
        mic_device_id: selectedMicDeviceId(),
        output_device_id: selectedOutputDeviceId(),
        screen: usesScreen,
        "display_indices": selectedDisplayIndices(),
        "screen_fps": selectedScreenFps(),
        "record_mouse": modeUsesMouse(),
        "record_keyboard": modeUsesKeyboard(),
      }),
    });
    setRecordingUi(true);
    activeMicDeviceValue = micDeviceSelect.value;
    activeOutputDeviceValue = outputDeviceSelect.value;
    recordingStartedAtMs = Date.now();
    updateRecordingTimerUi();
    setAppState(t("recordingActive"), "active");
    showToast(t("recordingStarted"), "success");
    setDynamicOutput(recordingOutput, () => `${t("recordingInProgress")}\n${formatRecordingPaths(result.recordings)}`, "success");
  } catch (error) {
    setRecordingUi(false);
    setAppState(t("recordingError"), "error");
    setOutput(recordingOutput, error.message, "error");
    showToast(t("recordingError"), "error");
  }
});

stopRecordButton.addEventListener("click", async () => {
  setOutput(recordingOutput, t("savingRecording"));
  stopRecordButton.disabled = true;

  try {
    const result = await requestJson("/api/record/stop", { method: "POST" });
    setRecordingUi(false);
    setAppState(t("recordingCompleted"), "success");
    showToast(t("recordingCompleted"), "success");
    const diagnosticsList = result.diagnostics_list || [result.diagnostics];
    recordingStartedAtMs = null;
    lastRecordingDurationSec = Number(result.duration_sec || Math.max(...diagnosticsList.map((item) => item.duration_sec || 0)));
    updateRecordingTimerUi();
    const hasWarnings = diagnosticsList.some((item) => item?.warnings?.length) || Boolean(result.errors?.length);
    setDynamicOutput(
      recordingOutput,
      () => formatAllDiagnostics(diagnosticsList, result.errors),
      hasWarnings ? "warning" : "success",
    );
    updateRecordingTranscribeActions(diagnosticsList);
    await refreshStorage();
  } catch (error) {
    setRecordingUi(false);
    setAppState(t("recordingError"), "error");
    setOutput(recordingOutput, error.message, "error");
    showToast(t("recordingError"), "error");
  }
});

refreshMicDevicesButton.addEventListener("click", () => refreshMicDevices(true));
refreshOutputDevicesButton.addEventListener("click", () => refreshOutputDevices(true));
for (const checkbox of recordingSourceCheckboxes) {
  checkbox.addEventListener("change", () => {
    updateModeUi();
    if (checkbox === screenSourceCheckbox && modeUsesScreen() && !displaysLoaded && !displayRefreshInFlight) {
      refreshDisplays(true);
    }
    refreshMicLevel();
    refreshSystemLevel();
  });
}
micDeviceSelect.addEventListener("change", handleMicDeviceChange);
outputDeviceSelect.addEventListener("change", handleOutputDeviceChange);
whisperModelSelect.addEventListener("change", () => {
  updateModelAvailabilityUi();
  renderRuntimeDetails();
});
for (const control of [defaultAudioEnabled, defaultFramesEnabled, defaultFrameRateSelect, defaultJpegQualitySelect, defaultFrameMaxSizeSelect, defaultOcrEnabled, defaultCvMetadataEnabled]) {
  control.addEventListener("change", () => {
    if (defaultOcrEnabled.checked) {
      defaultFramesEnabled.checked = true;
    }
    updateLongOperationControls();
    if (control === defaultFrameMaxSizeSelect) {
      void saveFrameSettings();
    }
  });
}
refreshModelsButton.addEventListener("click", async () => {
  refreshModelsButton.disabled = true;
  setModelManagerStatus(t("modelManagerLoading"), "info");
  try {
    await refreshModelStatuses();
    await refreshModelDownloadStatus(true);
    setModelManagerStatus(t("modelManagerReady"), "success");
  } finally {
    updateLongOperationControls();
  }
});
modelInfoCloseButton.addEventListener("click", hideModelInfo);
transcribeMicRecordingButton.addEventListener("click", () => addRecordingByType("mic"));
transcribeSystemRecordingButton.addEventListener("click", () => addRecordingByType("system"));
transcribeAllRecordingsButton.addEventListener("click", addAllRecordings);
openRecordingsButton.addEventListener("click", () => openFolder("recordings"));
openTranscriptsButton.addEventListener("click", () => openFolder("transcripts"));
openDataFolderButton.addEventListener("click", () => openFolder("data"));
transcriptPathForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadTranscript(transcriptPathInput.value, true, true);
});
refreshStorageSummaryButton.addEventListener("click", refreshStorageSummary);
keepDownloadedMediaCheckbox.addEventListener("change", saveStorageSettings);
keepUploadedTempCheckbox.addEventListener("change", saveStorageSettings);
clearDownloadsButton.addEventListener("click", () => cleanupStorageFolder("downloads"));
clearUploadsButton.addEventListener("click", () => cleanupStorageFolder("uploads"));
urlDownloadProfileSelect.addEventListener("change", syncUrlDownloadCustomField);
urlDownloadSaveButton.addEventListener("click", saveUrlDownloadSettings);
ocrCheckButton.addEventListener("click", checkOcrStatus);
videoMuxForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await mergeVideoWithAudio();
});
for (const select of [videoMuxVideoSelect, videoMuxMicSelect, videoMuxSystemSelect]) {
  select.addEventListener("change", setVideoMuxUi);
}
audioFilePickerButton.addEventListener("click", () => audioFileInput.click());
queueFilePickerButton.addEventListener("click", () => queueFileInput.click());
benchmarkFilePickerButton.addEventListener("click", () => benchmarkFileInput.click());
audioFileInput.addEventListener("change", () => updateFilePickerText(audioFileInput, audioFilePickerText));
queueFileInput.addEventListener("change", () => updateFilePickerText(queueFileInput, queueFilePickerText, true));
benchmarkFileInput.addEventListener("change", () => updateFilePickerText(benchmarkFileInput, benchmarkFilePickerText));
queueList.addEventListener("focusin", (event) => {
  if (!event.target.matches(queueControlSelector)) {
    return;
  }
  queueControlsFocused = true;
  window.clearTimeout(queueFocusRenderTimer);
});
queueList.addEventListener("focusout", () => {
  window.clearTimeout(queueFocusRenderTimer);
  queueFocusRenderTimer = window.setTimeout(() => {
    queueControlsFocused = queueControlHasActiveFocus();
    if (!queueControlsFocused && latestQueueStatus) {
      renderQueue(latestQueueStatus);
    }
  }, 150);
});
queueList.addEventListener("toggle", (event) => {
  const panel = event.target;
  if (panel.matches?.("[data-runtime-estimate-details-key]")) {
    const key = panel.dataset.runtimeEstimateDetailsKey;
    if (panel.open) {
      openRuntimeEstimateDetailsKeys.add(key);
    } else {
      openRuntimeEstimateDetailsKeys.delete(key);
    }
    return;
  }
  if (!panel.matches?.("[data-queue-settings-panel]")) {
    return;
  }
  const card = queueCardFromTarget(panel);
  const index = Number(card?.dataset.queueIndex);
  if (!index) {
    return;
  }
  if (panel.open) {
    collapsedQueueSettingsItemIds.delete(index);
  } else {
    collapsedQueueSettingsItemIds.add(index);
  }
}, true);
queueList.addEventListener("change", async (event) => {
  const target = event.target;
  if (!target.matches("[data-queue-operation], [data-queue-audio-model], [data-queue-audio-device], [data-queue-frame-rate], [data-queue-jpeg-quality], [data-queue-frame-size], [data-queue-url-max-height]")) {
    return;
  }
  await updateQueueItemFromCard(queueCardFromTarget(target));
});
queueList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-queue-action]");
  if (!button) {
    return;
  }
  const card = queueCardFromTarget(button);
  if (button.dataset.queueAction === "estimate") {
    await runRuntimeEstimate(card);
    return;
  }
  await removeOrCancelQueueItem(card, button.dataset.queueAction);
});
queueAddForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const files = Array.from(queueFileInput.files || []);
  await addLocalFilesToQueue(files, queueFileInput, queueFilePickerText, true);
});
queueUrlForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const urls = Array.from(new Map(
    queueUrlInput.value
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean)
      .map((url) => [normalizeQueueUrl(url), url]),
  ).values());
  if (!urls.length) {
    setOutput(queueOutput, t("selectAtLeastOneUrl"), "error");
    return;
  }
  const keys = urls.map(urlAddKey);
  if (isAddingUrl || hasPendingAddKey(keys)) {
    showAddStatus("queueUrlAlreadyAdding", "warning");
    return;
  }
  if (urls.some(activeQueueHasUrl)) {
    showAddStatus("queueUrlAlreadyQueued", "warning");
    return;
  }
  const processingPlan = defaultProcessingPlanSnapshot();
  isAddingUrl = true;
  rememberPendingAdd(keys);
  showAddStatus("queueStageAddingUrl");
  updateLongOperationControls();
  try {
    renderQueue(await requestJson("/api/queue/add-urls", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls, processing_plan: processingPlan, queue_folder_name: queueFolderNameValue() }),
    }));
    queueUrlInput.value = "";
    const message = t("urlAdded", { count: urls.length });
    setOutput(queueOutput, message, "success");
    showToast(message, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  } finally {
    isAddingUrl = false;
    forgetPendingAdd(keys);
    restoreQueueStageStatus();
    updateLongOperationControls();
  }
});
queueStartButton.addEventListener("click", async () => {
  if (!validateQueueStartOptions()) {
    return;
  }
  warnAboutSelectedModelDownload();
  try {
    renderQueue(await requestJson("/api/queue/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: selectedModel(), device: selectedDevice(), queue_folder_name: queueFolderNameValue() }),
    }));
    setLocalizedOutput(queueOutput, "queueStarted");
    showToast(t("queueStarted"), "info");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  }
});
queueStopButton.addEventListener("click", () => postQueueAction("/api/queue/stop-after-current", t("queueWillStop")));
queueClearButton.addEventListener("click", () => postQueueAction("/api/queue/clear", t("queueCleared")));
queueRetryButton.addEventListener("click", () => postQueueAction("/api/queue/retry-errors", t("queueRetried")));

benchmarkUploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = benchmarkFileInput.files[0];
  if (!file) {
    setOutput(benchmarkStatusOutput, t("selectBenchmarkFile"), "error");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  benchmarkUploadButton.disabled = true;
  try {
    const result = await requestJson("/api/benchmark/upload", { method: "POST", body: formData });
    benchmarkSourceId = result.source_id;
    setOutput(benchmarkStatusOutput, t("benchmarkPrepared", { name: result.source_filename }), "success");
  } catch (error) {
    benchmarkSourceId = null;
    setOutput(benchmarkStatusOutput, error.message, "error");
  } finally {
    updateLongOperationControls();
  }
});

for (const button of benchmarkButtons) {
  button.addEventListener("click", async () => {
    try {
      const device = button.dataset.benchmarkDevice;
      const mode = button.dataset.benchmarkMode;
      renderBenchmark(await requestJson("/api/benchmark/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_id: benchmarkSourceId, model: selectedModel(), device, mode }),
      }));
      setOutput(benchmarkStatusOutput, t("benchmarkStarted", { device, mode }));
    } catch (error) {
      setOutput(benchmarkStatusOutput, error.message, "error");
    }
  });
}

transcribeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await addLocalFilesToQueue(Array.from(audioFileInput.files || []), audioFileInput, audioFilePickerText);
});

async function boot() {
  populateDefaultProcessingControls();
  updateFilePickerText(audioFileInput, audioFilePickerText);
  updateFilePickerText(queueFileInput, queueFilePickerText, true);
  updateFilePickerText(benchmarkFileInput, benchmarkFilePickerText);
  updateModeUi();
  await loadDevices();
  await refreshStatus();
  await refreshModelStatuses();
  await refreshModelDownloadStatus(true);
  await refreshStorage();
  await refreshStorageSettings();
  await refreshFrameSettings();
  await refreshUrlDownloadSettings();
  await refreshOcrStatus();
  await refreshQueueStatus();
  await refreshBenchmarkStatus();
  await refreshMicLevel();
  await refreshSystemLevel();
  window.LocalMediaTranscriberTour?.maybePrompt();
}

boot();
setInterval(refreshMicLevel, 500);
setInterval(refreshSystemLevel, 500);
setInterval(refreshStatus, 5000);
setInterval(refreshStorage, 10000);
setInterval(updateRecordingTimerUi, 1000);
setInterval(refreshQueueStatus, 1000);
setInterval(refreshBenchmarkStatus, 1000);
setInterval(refreshModelDownloadStatus, 1000);

document.addEventListener("lat-language-change", () => {
  populateDefaultProcessingControls();
  updateFilePickerText(audioFileInput, audioFilePickerText);
  updateFilePickerText(queueFileInput, queueFilePickerText, true);
  updateFilePickerText(benchmarkFileInput, benchmarkFilePickerText);
  updateRecordingTimerUi();
  if (latestMicDevicesResult) {
    fillMicDevices(latestMicDevicesResult, micDeviceSelect.value);
  }
  if (latestOutputDevicesResult) {
    fillOutputDevices(latestOutputDevicesResult, outputDeviceSelect.value);
  }
  if (latestDisplays.length) {
    fillDisplays(latestDisplays, selectedDisplayIndices());
  }
  setRecordingUi(isRecording);
  renderModelManager();
  if (modelDownloadStatus) {
    renderModelDownloadStatus(modelDownloadStatus);
  }
  if (activeInfoModel) {
    showModelInfo(activeInfoModel);
  }
  if (latestQueueStatus) {
    renderQueue(latestQueueStatus);
  }
  renderRuntimeDetails();
  if (latestOcrStatus) {
    renderOcrStatus(latestOcrStatus);
  }
  rerenderDynamicOutputs();
  refreshStatus();
  refreshBenchmarkStatus();
  refreshStorage();
  refreshModelStatuses();
});
