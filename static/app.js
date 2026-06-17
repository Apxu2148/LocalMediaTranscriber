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
const transcriptText = document.querySelector("#transcriptText");
const systemStatus = document.querySelector("#systemStatus");
const modelBadge = document.querySelector("#modelBadge");
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
const toastRegion = document.querySelector("#toastRegion");
const appVersion = document.querySelector("#appVersion");
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
const queueOutput = document.querySelector("#queueOutput");
const queueList = document.querySelector("#queueList");
const queueUrlForm = document.querySelector("#queueUrlForm");
const queueUrlInput = document.querySelector("#queueUrlInput");
const queueUrlAddButton = document.querySelector("#queueUrlAddButton");
const queueSettingsSummary = document.querySelector("#queueSettingsSummary");
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
let benchmarkActive = false;
let benchmarkSourceId = null;
let videoMuxInFlight = false;
let overlayOwner = null;
let transcriptionPhase = null;
let activeRuntimeModel = null;
let lastLoadedQueueTranscriptPath = null;
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
const dynamicOutputRenderers = new Map();
const queueControlSelector = ".queue-item-card select, .queue-item-card input, .queue-item-card button";

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
  startRecordButton.disabled = recording || isTranscribing || queueActive || benchmarkActive || videoMuxInFlight;
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
  const blocked = videoMuxInFlight || isRecording || isTranscribing || queueActive || benchmarkActive;
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
    const message = payload?.detail?.message || payload?.message || t("requestError");
    const technicalDetails = payload?.detail?.technical_details || payload?.technical_details || "";
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
    const runtime = transcription.runtime_device || transcription.configured_device || "auto";
    const compute = transcription.runtime_compute_type || transcription.configured_compute_type || "auto";
    const model = transcription.active_model || transcription.loaded_model || selectedModel() || status.whisper_model;
    transcriptionPhase = transcription.phase || null;
    activeRuntimeModel = model;

    modelBadge.textContent = `Whisper ${model} · ${runtime}/${compute}`;
    updateRuntimeDetails({
      model,
      device: runtime,
      compute_type: compute,
      realtime_factor: null,
    });

    if (!whisperModelSelect.dataset.initialized && status.whisper_models?.includes(status.whisper_model)) {
      whisperModelSelect.value = status.whisper_model;
      whisperModelSelect.dataset.initialized = "true";
    }
    if (status.whisper_model_status) {
      applyModelStatuses(status.whisper_model_status);
    }
    deviceAvailabilityOutput.textContent = transcription.cuda_available ? t("cpuGpu") : t("cpuOnly");

    appVersion.textContent = `${t("version")}: ${status.app_version || "?"}`;
    syncRecordingTimer(status);
    isTranscribing = localTranscriptionActive || Boolean(transcription.in_progress);
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

function updateRuntimeDetails(benchmark) {
  if (!benchmark) {
    return;
  }

  runtimeModel.textContent = benchmark.model || selectedModel();
  runtimeDevice.textContent = benchmark.device || "auto";
  runtimeCompute.textContent = benchmark.compute_type || "auto";
  if (benchmark.realtime_factor !== null && benchmark.realtime_factor !== undefined) {
    runtimeSpeed.textContent = `${benchmark.realtime_factor}x`;
  }
}

function updateRecordingTranscribeActions(recordings) {
  lastRecordings = recordings || [];
  const micRecording = lastRecordings.find((item) => item.source_type === "mic");
  const systemRecording = lastRecordings.find((item) => item.source_type === "system");
  const audioRecordings = lastRecordings.filter((item) => item.source_type === "mic" || item.source_type === "system");
  const blocked = isTranscribing || queueActive || benchmarkActive;
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
  try {
    const status = await requestJson("/api/queue/add-recordings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        files: recordings.map((item) => ({
          file_path: item.audio_file,
          source_type: item.source_type,
        })),
      }),
    });
    renderQueue(status);
    const message = t("recordingsAdded", { count: recordings.length });
    setOutput(queueOutput, message, "success");
    showToast(message, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  }
}

async function addLocalFilesToQueue(files, input, pickerText, multiple = false) {
  if (!files.length) {
    setOutput(queueOutput, t(multiple ? "selectAtLeastOneFile" : "selectFile"), "error");
    return;
  }
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  try {
    renderQueue(await requestJson("/api/queue/add-files", { method: "POST", body: formData }));
    resetFilePicker(input, pickerText, multiple);
    const message = t("filesAdded", { count: files.length });
    setOutput(queueOutput, message, "success");
    showToast(message, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  }
}

function transcriptFileName(value) {
  const text = String(value || "");
  return text.split(/[\\/]/).filter(Boolean).pop() || text;
}

async function loadTranscript(filePath, announce = false) {
  const transcriptName = transcriptFileName(filePath);
  try {
    const result = await requestJson(`/api/transcripts/read?file_path=${encodeURIComponent(transcriptName)}`);
    transcriptText.value = result.text || "";
    lastLoadedQueueTranscriptPath = filePath;
    if (announce) {
      setDynamicOutput(transcribeOutput, () => t("transcriptLoaded", { name: transcriptName }), "success");
    }
  } catch (error) {
    setOutput(transcribeOutput, error.message, "error");
  }
}

function maybeLoadLatestQueueTranscript(status) {
  const completedItem = [...(status.items || [])]
    .reverse()
    .find((item) => ["completed", "error", "failed"].includes(item.status) && item.transcript_path);
  if (completedItem?.transcript_path && completedItem.transcript_path !== lastLoadedQueueTranscriptPath) {
    loadTranscript(completedItem.transcript_path);
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

async function refreshStorage() {
  try {
    const storage = await requestJson("/api/storage");
    diskFree.textContent = t("diskFree", { value: storage.disk?.free_gb ?? "?" });
    recordingsPath.textContent = storage.recordings.path;
    transcriptsPath.textContent = storage.transcripts.path;
    latestRecordingFiles = storage.recordings.files || [];
    renderFileList(recordingsFileList, latestRecordingFiles, t("recordingsEmpty"));
    renderFileList(transcriptsFileList, storage.transcripts.files, t("transcriptsEmpty"), true);
    fillVideoMuxOptions(latestRecordingFiles);
  } catch (error) {
    renderFileList(recordingsFileList, [], error.message);
    renderFileList(transcriptsFileList, [], error.message);
    latestRecordingFiles = [];
    fillVideoMuxOptions([]);
  }
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
      name.addEventListener("click", () => loadTranscript(file.name, true));
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

  for (const option of whisperModelSelect.options) {
    const status = modelStatusByName.get(option.value);
    if (!status) {
      continue;
    }
    option.textContent = `${status.name} - ${modelOptionDescription(status.name)} (${isModelDownloaded(status) ? t("modelLocal") : t("modelNotDownloaded")})`;
  }

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

function modelSizeLabel(model) {
  return t(`modelSize${modelKeyPrefix(model)}`);
}

function modelInfoFieldKey(model, field) {
  return `modelInfo${modelKeyPrefix(model)}${field}`;
}

function isModelDownloaded(status) {
  return Boolean(status?.local || status?.is_downloaded || status?.status === "available");
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
    return overrideStatus;
  }
  if (status?.status === "starting" || (modelDownloadStatus?.status === "starting" && modelDownloadStatus.model === name)) {
    return "starting";
  }
  if (status?.status === "downloading" || (modelDownloadStatus?.active && modelDownloadStatus.model === name)) {
    return "downloading";
  }
  if (status?.status === "download_error") {
    return "download_error";
  }
  return isModelDownloaded(status) ? "available" : "not_downloaded";
}

function modelStatusLabel(statusCode) {
  return {
    available: t("modelStatusAvailable"),
    starting: t("modelStatusStarting"),
    not_downloaded: t("modelStatusNotDownloaded"),
    downloading: t("modelStatusDownloading"),
    verifying: t("modelStatusVerifying"),
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
    modelDownloadProgressBlock.hidden = true;
    modelDownloadProgress.removeAttribute("value");
    setModelManagerStatus(t("modelDownloadFailed"), "error");
  } else if (status?.status === "available" && status.model) {
    modelDownloadProgressBlock.hidden = true;
    modelDownloadProgress.value = 100;
    setModelManagerStatus(t("modelDownloadCompleted", { model: status.model }), "success");
  } else if (!modelManagerStatus.textContent) {
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
    setModelManagerStatus(t("modelDownloadFailed"), "error");
    showToast(t("modelDownloadFailed"), "error");
    renderModelManager();
  }
}

async function verifyModel(model) {
  verifyingModels.add(model);
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
    } else {
      modelOperationStatusByName.set(model, result.status === "not_downloaded" ? "not_downloaded" : "verification_error");
      const message = result.status === "not_downloaded" ? t("modelVerifyNeedsDownload") : t("modelVerifyFailed");
      setModelManagerStatus(message, "error");
      showToast(message, "error");
    }
  } catch (error) {
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
    transcribing: t("statusTranscribing"),
    completed: t("statusCompleted"),
    error: t("statusError"),
    failed: t("statusError"),
    cancelled: t("statusCancelled"),
  }[status] || status;
}

function updateQueueSettingsSummary(status = null) {
  queueSettingsSummary.textContent = t("queueSnapshot", {
    model: status?.model || selectedModel(),
    device: status?.device_preference || selectedDevice(),
  });
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

  wrapper.append(rateLabel, qualityLabel, estimate);
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
  const downloadedMediaPath = queueItem.downloaded_media_path || queueItem.downloaded_video_path;
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
  item.className = "queue-item-card";
  item.dataset.queueIndex = String(queueItem.index);
  item.dataset.mediaKind = queueItem.media_kind || (queueItemIsVideo(queueItem) ? "video" : "audio");

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
  const canCancel = isCurrent && queueItem.status === "extracting_frames";
  const currentButCannotCancel = isCurrent && !canCancel && status.status === "running";
  if (canRemove || canCancel || currentButCannotCancel) {
    const actionButton = document.createElement("button");
    actionButton.type = "button";
    actionButton.className = canCancel || currentButCannotCancel
      ? "queue-item-remove queue-item-cancel"
      : "queue-item-remove";
    actionButton.textContent = canRemove ? "\u00d7" : t("cancelCurrentShort");
    actionButton.dataset.queueAction = canCancel ? "cancel" : "remove";
    actionButton.disabled = currentButCannotCancel;
    actionButton.title = canCancel
      ? t("cancelCurrentItem")
      : currentButCannotCancel
        ? t("runningAudioCannotCancel")
        : t("removeFromQueue");
    actionButton.setAttribute("aria-label", actionButton.title);
    headerActions.append(actionButton);
  }

  header.append(titleBlock, headerActions);
  item.append(header);

  const options = queueItem.operations || {};
  const controlsDisabled = queueActive || queueItem.status !== "pending";
  const optionGroup = document.createElement("div");
  optionGroup.className = "queue-options";
  if (queueItemIsVideo(queueItem)) {
    const label = document.createElement("div");
    label.className = "queue-options-label";
    label.textContent = t("processingOptions");
    optionGroup.append(
      label,
      createQueueCheckbox("transcribeAudio", options.transcribe_audio, controlsDisabled, "transcribe_audio"),
      createQueueCheckbox("extractFrames", options.extract_frames, controlsDisabled, "extract_frames"),
      createFrameSettings(queueItem, controlsDisabled),
      createComingSoonOption("ocr"),
      createComingSoonOption("cv"),
    );
  } else {
    optionGroup.append(createQueueCheckbox("transcribeAudio", true, true, "transcribe_audio"));
  }
  item.append(optionGroup);

  const outputLines = queueItemOutputLines(queueItem);
  if (outputLines.length) {
    const resultBlock = document.createElement("div");
    resultBlock.className = "queue-frame-result";
    resultBlock.append(...outputLines.map((line) => textLine(line)));
    item.append(resultBlock);
  }

  if (queueItem.error_message) {
    const error = document.createElement("p");
    error.className = "queue-item-error";
    error.textContent = formatQueueItemError(queueItem);
    item.append(error);
  }

  item.title = formatQueueItemError(queueItem) || translateUiText(queueItem.source_url || queueItem.source_path || "");
  return item;
}

function renderQueue(status, options = {}) {
  latestQueueStatus = status;
  queueActive = status.status === "running";
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

  queueAddButton.disabled = queueActive;
  queueFileInput.disabled = queueActive;
  queueFilePickerButton.disabled = queueActive;
  queueUrlAddButton.disabled = queueActive;
  queueUrlInput.disabled = queueActive;
  queueStartButton.disabled = queueActive || pending === 0;
  queueStopButton.disabled = !queueActive || Boolean(status.stop_after_current);
  queueClearButton.disabled = queueActive || total === 0;
  queueRetryButton.disabled = queueActive || failed === 0;
  whisperModelSelect.disabled = queueActive;
  whisperDeviceSelect.disabled = queueActive;
  transcribeButton.disabled = queueActive || isTranscribing;
  setRecordingUi(isRecording);
  updateRecordingTranscribeActions(lastRecordings);
  updateQueueSettingsSummary(queueActive ? status : null);

  if (queueActive) {
    const current = status.current_item || {};
    const modelLoading = transcriptionPhase === "loading_model" && !modelStatusByName.get(activeRuntimeModel)?.local;
    showOperation(
      "queue",
      current.status === "downloading"
        ? t("urlDownloading")
        : modelLoading
          ? t("modelDownloading", { model: activeRuntimeModel })
          : t("queueRunning"),
      modelLoading ? t("modelDownloadText") : t("queueOverlay", {
        done: finished,
        total,
        item: status.current_file || "-",
        stage: queueStatusLabel(current.status || "pending"),
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

  const latestCompletedItem = [...(status.items || [])]
    .reverse()
    .find((item) => item.status === "completed");
  if (status.model) {
    runtimeModel.textContent = status.model;
  }
  if (status.device_preference) {
    runtimeDevice.textContent = status.device_preference;
  }
  if (latestCompletedItem?.realtime_factor !== null && latestCompletedItem?.realtime_factor !== undefined) {
    runtimeSpeed.textContent = `${latestCompletedItem.realtime_factor}x`;
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
    ocr: false,
    cv: false,
  };
  const rateSelect = card.querySelector("[data-queue-frame-rate]");
  const qualitySelect = card.querySelector("[data-queue-jpeg-quality]");
  return {
    index: Number(card.dataset.queueIndex),
    operations,
    frame_extraction: {
      rate: frameRateFromValue(rateSelect?.value),
      jpeg_quality: Number(qualitySelect?.value || 90),
    },
  };
}

async function updateQueueItemFromCard(card) {
  if (!card || queueActive) {
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

async function removeOrCancelQueueItem(card, action) {
  if (!card) {
    return;
  }
  const index = Number(card.dataset.queueIndex);
  const url = action === "cancel" ? "/api/queue/cancel-item" : "/api/queue/remove-item";
  try {
    renderQueue(await requestJson(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ index }),
    }));
    const message = action === "cancel" ? t("queueItemCancelRequested") : t("queueItemRemoved");
    setOutput(queueOutput, message, action === "cancel" ? "warning" : "success");
    showToast(message, action === "cancel" ? "warning" : "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  }
}

function validateQueueStartOptions() {
  const invalid = (latestQueueStatus?.items || []).find((item) => {
    const operations = item.operations || {};
    return item.status === "pending"
      && queueItemIsVideo(item)
      && !operations.transcribe_audio
      && !operations.extract_frames;
  });
  if (!invalid) {
    return true;
  }
  const message = invalid.source_type === "url" ? t("selectAtLeastOneUrlOperation") : t("selectAtLeastOneVideoOperation");
  setOutput(queueOutput, message, "error");
  showToast(message, "error");
  return false;
}

function updateLongOperationControls() {
  const active = isTranscribing || queueActive || benchmarkActive || videoMuxInFlight;
  whisperModelSelect.disabled = active;
  whisperDeviceSelect.disabled = active;
  transcribeButton.disabled = active;
  audioFileInput.disabled = active;
  audioFilePickerButton.disabled = active;
  queueAddButton.disabled = active;
  queueFileInput.disabled = active;
  queueFilePickerButton.disabled = active;
  queueUrlAddButton.disabled = active;
  queueUrlInput.disabled = active;
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
  runtimeModel.textContent = selectedModel();
  updateModelAvailabilityUi();
  updateQueueSettingsSummary();
});
whisperDeviceSelect.addEventListener("change", updateQueueSettingsSummary);
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
queueList.addEventListener("change", async (event) => {
  const target = event.target;
  if (!target.matches("[data-queue-operation], [data-queue-frame-rate], [data-queue-jpeg-quality]")) {
    return;
  }
  await updateQueueItemFromCard(queueCardFromTarget(target));
});
queueList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-queue-action]");
  if (!button) {
    return;
  }
  await removeOrCancelQueueItem(queueCardFromTarget(button), button.dataset.queueAction);
});
queueAddForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const files = Array.from(queueFileInput.files || []);
  await addLocalFilesToQueue(files, queueFileInput, queueFilePickerText, true);
});
queueUrlForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const urls = queueUrlInput.value.split(/\r?\n/).map((value) => value.trim()).filter(Boolean);
  if (!urls.length) {
    setOutput(queueOutput, t("selectAtLeastOneUrl"), "error");
    return;
  }
  queueUrlAddButton.disabled = true;
  try {
    renderQueue(await requestJson("/api/queue/add-urls", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ urls }),
    }));
    queueUrlInput.value = "";
    const message = t("urlAdded", { count: urls.length });
    setOutput(queueOutput, message, "success");
    showToast(message, "success");
  } catch (error) {
    setOutput(queueOutput, error.message, "error");
    showToast(error.message, "error");
  } finally {
    queueUrlAddButton.disabled = queueActive;
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
      body: JSON.stringify({ model: selectedModel(), device: selectedDevice() }),
    }));
    setOutput(queueOutput, t("queueStarted"));
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
  updateFilePickerText(audioFileInput, audioFilePickerText);
  updateFilePickerText(queueFileInput, queueFilePickerText, true);
  updateFilePickerText(benchmarkFileInput, benchmarkFilePickerText);
  updateModeUi();
  await loadDevices();
  await refreshStatus();
  await refreshModelStatuses();
  await refreshModelDownloadStatus(true);
  await refreshStorage();
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
  updateQueueSettingsSummary(queueActive ? latestQueueStatus : null);
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
  rerenderDynamicOutputs();
  refreshStatus();
  refreshBenchmarkStatus();
  refreshStorage();
  refreshModelStatuses();
});
