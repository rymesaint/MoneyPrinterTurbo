<template>
  <div class="shell">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect x="2" y="4" width="20" height="16" rx="3" stroke="var(--brand)" stroke-width="1.5" fill="none"/>
            <polygon points="10,9 16,12 10,15" fill="var(--brand)"/>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">MoneyPrinter</span>
          <span class="brand-tag">Turbo</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button class="nav-item" :class="{ active: activeTab === 'create' }" @click="activeTab = 'create'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 1a1 1 0 011 1v5h5a1 1 0 110 2H9v5a1 1 0 11-2 0V9H2a1 1 0 010-2h5V2a1 1 0 011-1z"/></svg>
          {{ tr('Create Video') }}
        </button>
        <button class="nav-item" :class="{ active: activeTab === 'tasks' }" @click="activeTab = 'tasks'">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M2 3h12v2H2V3zm0 4h12v2H2V7zm0 4h8v2H2v-2z"/></svg>
          {{ tr('Tasks') }}
        </button>
        <button class="nav-item" :class="{ active: activeTab === 'youtube' }" @click="activeTab = 'youtube'; loadYoutubeData()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"></path>
            <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" fill="currentColor"></polygon>
          </svg>
          {{ tr('YouTube Stats') }}
        </button>
        <button class="nav-item" :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          {{ tr('Settings') }}
        </button>
      </nav>

      <div class="sidebar-footer">
        <select v-model="locale" class="locale-picker" @change="onLocaleChange">
          <option v-for="l in localeList" :key="l.code" :value="l.code">{{ l.name }}</option>
        </select>
      </div>
    </aside>

    <!-- Main -->
    <main class="main">
      <!-- Top bar -->
      <header class="topbar">
        <h1 class="page-title">
          {{ activeTab === 'create' ? tr('Create Video') : activeTab === 'tasks' ? tr('Tasks') : activeTab === 'youtube' ? tr('YouTube Stats') : tr('Settings') }}
        </h1>
      </header>

      <!-- Create form -->
      <div v-if="activeTab === 'create'" class="content">
        <!-- Hero input -->
        <section class="hero-input">
          <label class="hero-label">{{ tr('Video Subject') }}</label>
          <div class="hero-field">
            <input
              v-model="form.video_subject"
              type="text"
              class="hero-text"
              :placeholder="tr('What is your video about?')"
            />
            <button class="btn-hero" :disabled="generating || !form.video_subject" @click="generateScriptAndTerms">
              <span v-if="generating" class="spinner"></span>
              <template v-else>{{ tr('Generate Script') }}</template>
            </button>
          </div>
        </section>

        <!-- Two-column settings -->
        <div class="settings-grid">
          <!-- Left: Script + Video -->
          <div class="settings-col">
            <!-- Script output -->
            <section class="section" v-if="form.video_script || form.video_terms">
              <h2 class="section-title">{{ tr('Generated Script') }}</h2>
              <div class="field">
                <label class="field-label">{{ tr('Video Script') }}</label>
                <textarea v-model="form.video_script" class="control textarea" rows="8"></textarea>
              </div>
              <div class="field">
                <label class="field-label">{{ tr('Video Keywords') }}</label>
                <textarea v-model="form.video_terms" class="control textarea" rows="2"></textarea>
              </div>
            </section>

            <!-- Script config -->
            <section class="section">
              <h2 class="section-title">{{ tr('Script Settings') }}</h2>
              <div class="field-group">
                <div class="field">
                  <label class="field-label">{{ tr('Script Language') }}</label>
                  <select v-model="form.video_language" class="control select">
                    <option value="">{{ tr('Auto Detect') }}</option>
                    <option v-for="lang in supportLocales" :key="lang" :value="lang">{{ lang }}</option>
                  </select>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Paragraphs') }}</label>
                  <div class="range-field">
                    <input v-model.number="form.paragraph_number" type="range" min="1" max="10" class="range" />
                    <span class="range-badge">{{ form.paragraph_number }}</span>
                  </div>
                </div>
              </div>
              <div class="field">
                <label class="field-label">{{ tr('Custom Script Requirements') }}</label>
                <textarea v-model="form.video_script_prompt" class="control textarea" rows="2" :placeholder="tr('Custom Script Requirements Placeholder')"></textarea>
              </div>
            </section>

            <!-- Video settings -->
            <section class="section">
              <h2 class="section-title">{{ tr('Video Settings') }}</h2>
              <div class="field-group">
                <div class="field">
                  <label class="field-label">{{ tr('Video Source') }}</label>
                  <select v-model="form.video_source" class="control select">
                    <option value="pexels">Pexels</option>
                    <option value="pixabay">Pixabay</option>
                    <option value="coverr">Coverr</option>
                    <option value="vecteezy">Vecteezy</option>
                    <option value="local">{{ tr('Local file') }}</option>
                  </select>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Aspect Ratio') }}</label>
                  <div class="ratio-picker">
                    <button
                      class="ratio-btn"
                      :class="{ active: form.video_aspect === '9:16' }"
                      @click="form.video_aspect = '9:16'"
                    >
                      <span class="ratio-icon portrait"></span>
                      9:16
                    </button>
                    <button
                      class="ratio-btn"
                      :class="{ active: form.video_aspect === '16:9' }"
                      @click="form.video_aspect = '16:9'"
                    >
                      <span class="ratio-icon landscape"></span>
                      16:9
                    </button>
                  </div>
                </div>
              </div>
              <div class="field-group triple">
                <div class="field">
                  <label class="field-label">{{ tr('Clip Duration') }}</label>
                  <select v-model.number="form.video_clip_duration" class="control select">
                    <option v-for="d in [2,3,4,5,6,7,8,9,10]" :key="d" :value="d">{{ d }}s</option>
                  </select>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Count') }}</label>
                  <select v-model.number="form.video_count" class="control select">
                    <option v-for="n in [1,2,3,4,5]" :key="n" :value="n">{{ n }}</option>
                  </select>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Concat') }}</label>
                  <select v-model="form.video_concat_mode" class="control select">
                    <option value="random">{{ tr('Random') }}</option>
                    <option value="sequential">{{ tr('Sequential') }}</option>
                  </select>
                </div>
              </div>
              <div class="field">
                <label class="field-label">{{ tr('Transition') }}</label>
                <select v-model="form.video_transition_mode" class="control select">
                  <option :value="null">{{ tr('None') }}</option>
                  <option value="Shuffle">{{ tr('Shuffle') }}</option>
                  <option value="FadeIn">{{ tr('Fade In') }}</option>
                  <option value="FadeOut">{{ tr('Fade Out') }}</option>
                </select>
              </div>
              <div class="field" style="margin-top:var(--sp-4)">
                <label class="field-label">{{ tr('Schedule YouTube Publish') }} ({{ tr('Optional') }})</label>
                <input
                  v-model="form.publish_at"
                  type="datetime-local"
                  class="control input"
                />
              </div>
            </section>
          </div>

          <!-- Right: Audio + Subtitles -->
          <div class="settings-col">
            <!-- Audio -->
            <section class="section">
              <h2 class="section-title">{{ tr('Audio Settings') }}</h2>
              <div class="field">
                <label class="field-label">{{ tr('TTS Engine') }}</label>
                <select v-model="form.tts_server" class="control select" @change="loadVoices">
                  <option value="no-voice">{{ tr('No Voice') }}</option>
                  <option value="azure-tts-v1">{{ tr('Azure TTS V1') }}</option>
                  <option value="azure-tts-v2">{{ tr('Azure TTS V2') }}</option>
                  <option value="siliconflow">{{ tr('SiliconFlow') }}</option>
                  <option value="gemini-tts">{{ tr('Gemini TTS') }}</option>
                  <option value="mimo-tts">{{ tr('MiMo TTS') }}</option>
                  <option value="elevenlabs">{{ tr('ElevenLabs') }}</option>
                </select>
              </div>
              <div class="field" v-if="form.tts_server !== 'no-voice'">
                <label class="field-label">{{ tr('Voice') }}</label>
                <div style="display: flex; gap: var(--sp-2);">
                  <select v-model="form.voice_name" class="control select" style="flex: 1;">
                    <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.name }}</option>
                  </select>
                  <button
                    class="btn-preview-voice"
                    @click="playVoicePreview"
                    :disabled="previewingVoice || !form.voice_name"
                    style="flex-shrink: 0;"
                  >
                    <span v-if="previewingVoice" class="spinner" style="width: 14px; height: 14px;"></span>
                    <template v-else>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                      </svg>
                      {{ tr('Listen') }}
                    </template>
                  </button>
                </div>
              </div>
              <div class="field-group" v-if="form.tts_server !== 'no-voice'">
                <div class="field">
                  <label class="field-label">{{ tr('Speed') }}</label>
                  <select v-model.number="form.voice_rate" class="control select">
                    <option v-for="r in [0.8,0.9,1.0,1.1,1.2,1.3,1.5,1.8,2.0]" :key="r" :value="r">{{ r }}×</option>
                  </select>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Volume') }}</label>
                  <select v-model.number="form.voice_volume" class="control select">
                    <option v-for="v in [0.6,0.8,1.0,1.2,1.5,2.0]" :key="v" :value="v">{{ v }}</option>
                  </select>
                </div>
              </div>
              <div class="field-group">
                <div class="field">
                  <label class="field-label">{{ tr('Background Music') }}</label>
                  <select v-model="form.bgm_type" class="control select">
                    <option value="">{{ tr('None') }}</option>
                    <option value="random">{{ tr('Random') }}</option>
                    <option value="ccmixter">ccMixter</option>
                  </select>
                </div>
                <div class="field" v-if="form.bgm_type">
                  <label class="field-label">{{ tr('BGM Volume') }}</label>
                  <div class="range-field">
                    <input v-model.number="form.bgm_volume" type="range" min="0" max="1" step="0.05" class="range" />
                    <span class="range-badge">{{ form.bgm_volume.toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </section>

            <!-- Subtitles -->
            <section class="section">
              <h2 class="section-title">
                {{ tr('Subtitles') }}
                <label class="toggle-wrap">
                  <input type="checkbox" v-model="form.subtitle_enabled" class="toggle-input" />
                  <span class="toggle-track"><span class="toggle-thumb"></span></span>
                </label>
              </h2>
              <template v-if="form.subtitle_enabled">
                <div class="field-group">
                  <div class="field">
                    <label class="field-label">{{ tr('Font') }}</label>
                    <select v-model="form.font_name" class="control select">
                      <option v-for="f in fonts" :key="f" :value="f">{{ f }}</option>
                    </select>
                  </div>
                  <div class="field">
                    <label class="field-label">{{ tr('Position') }}</label>
                    <select v-model="form.subtitle_position" class="control select">
                      <option value="top">{{ tr('Top') }}</option>
                      <option value="center">{{ tr('Center') }}</option>
                      <option value="bottom">{{ tr('Bottom') }}</option>
                    </select>
                  </div>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Font Size') }}</label>
                  <div class="range-field">
                    <input v-model.number="form.font_size" type="range" min="30" max="100" class="range" />
                    <span class="range-badge">{{ form.font_size }}px</span>
                  </div>
                </div>
                <div class="field-group">
                  <div class="field">
                    <label class="field-label">{{ tr('Text Color') }}</label>
                    <div class="color-field">
                      <input type="color" v-model="form.text_fore_color" class="color-swatch" />
                      <span class="color-hex">{{ form.text_fore_color }}</span>
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">{{ tr('Stroke') }}</label>
                    <div class="color-field">
                      <input type="color" v-model="form.stroke_color" class="color-swatch" />
                      <span class="color-hex">{{ form.stroke_width }}px</span>
                    </div>
                  </div>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Stroke Width') }}</label>
                  <div class="range-field">
                    <input v-model.number="form.stroke_width" type="range" min="0" max="10" step="0.5" class="range" />
                    <span class="range-badge">{{ form.stroke_width }}</span>
                  </div>
                </div>
              </template>
            </section>

            <!-- Generate CTA -->
            <button class="btn-generate" :disabled="isGenerating || (!form.video_subject && !form.video_script)" @click="generateVideo">
              <span v-if="isGenerating" class="spinner"></span>
              <template v-else>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style="margin-right:6px">
                  <polygon points="4,2 16,9 4,16" fill="currentColor"/>
                </svg>
                {{ tr('Generate Video') }}
              </template>
            </button>
          </div>
        </div>

        <!-- Task panel (inline, below settings) -->
        <section v-if="activeTask" class="task-monitor">
          <div class="task-head">
            <div class="task-info">
              <span class="task-badge" :class="taskBadgeClass">{{ taskStatusLabel }}</span>
              <span class="task-id">{{ activeTask.task_id?.slice(0, 8) }}</span>
            </div>
            <span class="task-pct" :style="{ color: taskPctColor }">{{ activeTask.progress ?? 0 }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-bar" :style="{ width: (activeTask.progress ?? 0) + '%' }"></div>
          </div>
          <div v-if="taskLog" class="terminal">
            <pre>{{ taskLog }}</pre>
          </div>
          <div v-if="activeTask.state === 1 && activeTask.videos" class="results">
            <div v-for="(vid, i) in activeTask.videos" :key="i" class="result-item">
              <video :src="vid" controls class="result-video"></video>
            </div>
          </div>
        </section>
      </div>

      <!-- Tasks list -->
      <div v-else-if="activeTab === 'tasks'" class="content">
        <div v-if="loadingTasks" class="loading-state">
          <span class="spinner"></span>
          <span class="loading-text">{{ tr('Loading tasks...') }}</span>
        </div>
        <template v-else>
          <!-- Empty State -->
          <div v-if="tasks.length === 0" class="empty-state">
            <div class="empty-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2v20M2 12h20M12 12m-6 0a6 6 0 1 0 12 0 6 6 0 1 0-12 0" opacity="0.3" />
                <rect x="8" y="8" width="8" height="8" rx="1" fill="currentColor" fill-opacity="0.1" />
              </svg>
            </div>
            <h3 class="empty-title">{{ tr('Your screening room is quiet') }}</h3>
            <p class="empty-desc">{{ tr('Generate a script and create a video to start your cinematic catalog.') }}</p>
            <button class="btn-hero" @click="activeTab = 'create'">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" style="margin-right:6px">
                <path d="M8 1a1 1 0 011 1v5h5a1 1 0 110 2H9v5a1 1 0 11-2 0V9H2a1 1 0 010-2h5V2a1 1 0 011-1z"/>
              </svg>
              {{ tr('Create Video') }}
            </button>
          </div>

          <!-- Tasks list grid -->
          <div v-else class="tasks-grid">
            <div v-for="t in tasks" :key="t.task_id" class="task-card">
              <div class="task-card-header">
                <div class="task-card-info">
                  <span class="task-badge" :class="getTaskBadgeClass(t.state)">{{ getTaskStatusLabel(t.state) }}</span>
                  <span class="task-card-id" :title="t.task_id">{{ t.task_id?.slice(0, 8) }}</span>
                </div>
                <div class="task-card-actions">
                  <button class="btn-icon" :title="tr('View Logs')" @click="viewTaskLogs(t)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                      <polyline points="14 2 14 8 20 8"></polyline>
                      <line x1="16" y1="13" x2="8" y2="13"></line>
                      <line x1="16" y1="17" x2="8" y2="17"></line>
                      <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                  </button>
                  <button class="btn-icon delete" :title="tr('Delete Task')" @click="confirmDeleteTask(t.task_id)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      <line x1="10" y1="11" x2="10" y2="17"></line>
                      <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Content of the task -->
              <div class="task-card-body">
                <h4 v-if="t.video_subject" class="task-card-subject">{{ t.video_subject }}</h4>
                <p v-else-if="t.video_script" class="task-card-script-preview">{{ truncateText(t.video_script, 100) }}</p>
                <p v-else class="task-card-no-subject">{{ tr('No Subject Specified') }}</p>
              </div>

              <!-- Progress for in-progress tasks -->
              <div class="task-card-progress-section" v-if="t.state === 4">
                <div class="task-card-pct-row">
                  <span>{{ tr('Progress') }}</span>
                  <span class="task-card-pct">{{ t.progress ?? 0 }}%</span>
                </div>
                <div class="progress-track">
                  <div class="progress-bar" :style="{ width: (t.progress ?? 0) + '%' }"></div>
                </div>
              </div>

              <!-- Results video preview if completed -->
              <div v-if="t.state === 1 && t.videos && t.videos.length" class="task-card-video">
                <video :src="t.videos[0]" controls class="result-video"></video>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Settings Tab -->
      <div v-else-if="activeTab === 'settings'" class="content">
        <div class="settings-container">
          <div class="settings-sidebar">
            <button class="settings-nav-btn" :class="{ active: activeSettingsTab === 'llm' }" @click="activeSettingsTab = 'llm'">{{ tr('LLM Providers') }}</button>
            <button class="settings-nav-btn" :class="{ active: activeSettingsTab === 'materials' }" @click="activeSettingsTab = 'materials'">{{ tr('Material Keys') }}</button>
            <button class="settings-nav-btn" :class="{ active: activeSettingsTab === 'integrations' }" @click="activeSettingsTab = 'integrations'">{{ tr('Integrations') }}</button>
            <button class="settings-nav-btn" :class="{ active: activeSettingsTab === 'system' }" @click="activeSettingsTab = 'system'">{{ tr('System Settings') }}</button>
          </div>

          <div class="settings-content">
            <!-- LLM Provider Settings -->
            <div v-if="activeSettingsTab === 'llm'" class="settings-section-panel">
              <h2 class="settings-panel-title">{{ tr('LLM Providers') }}</h2>
              
              <div class="field">
                <label class="field-label">{{ tr('Active LLM Provider') }}</label>
                <select v-model="configData.app.llm_provider" class="control select">
                  <option value="deepseek">DeepSeek</option>
                  <option value="openai">OpenAI</option>
                  <option value="gemini">Gemini</option>
                  <option value="groq">Groq</option>
                  <option value="grok">Grok</option>
                  <option value="qwen">Qwen (Aliyun)</option>
                  <option value="minimax">MiniMax</option>
                  <option value="mimo">MiMo</option>
                  <option value="oneapi">OneAPI</option>
                  <option value="litellm">LiteLLM</option>
                </select>
              </div>

              <!-- DeepSeek -->
              <div v-if="configData.app.llm_provider === 'deepseek'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('DeepSeek API Key') }}</label>
                  <input v-model="configData.app.deepseek_api_key" type="password" class="control input" placeholder="sk-..." />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('DeepSeek Base URL') }}</label>
                  <input v-model="configData.app.deepseek_base_url" type="text" class="control input" placeholder="http://localhost:20128/v1" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('DeepSeek Model Name') }}</label>
                  <input v-model="configData.app.deepseek_model_name" type="text" class="control input" placeholder="deepseek-chat" />
                </div>
              </div>

              <!-- OpenAI -->
              <div v-if="configData.app.llm_provider === 'openai'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('OpenAI API Key') }}</label>
                  <input v-model="configData.app.openai_api_key" type="password" class="control input" placeholder="sk-..." />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('OpenAI Base URL') }}</label>
                  <input v-model="configData.app.openai_base_url" type="text" class="control input" placeholder="https://api.openai.com/v1" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('OpenAI Model Name') }}</label>
                  <input v-model="configData.app.openai_model_name" type="text" class="control input" placeholder="gpt-4o-mini" />
                </div>
              </div>

              <!-- Gemini -->
              <div v-if="configData.app.llm_provider === 'gemini'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('Gemini API Key') }}</label>
                  <input v-model="configData.app.gemini_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Gemini Model Name') }}</label>
                  <input v-model="configData.app.gemini_model_name" type="text" class="control input" placeholder="gemini-2.5-flash" />
                </div>
              </div>

              <!-- Groq -->
              <div v-if="configData.app.llm_provider === 'groq'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('Groq API Key') }}</label>
                  <input v-model="configData.app.groq_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Groq Base URL') }}</label>
                  <input v-model="configData.app.groq_base_url" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Groq Model Name') }}</label>
                  <input v-model="configData.app.groq_model_name" type="text" class="control input" />
                </div>
              </div>

              <!-- Grok -->
              <div v-if="configData.app.llm_provider === 'grok'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('Grok API Key') }}</label>
                  <input v-model="configData.app.grok_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Grok Base URL') }}</label>
                  <input v-model="configData.app.grok_base_url" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Grok Model Name') }}</label>
                  <input v-model="configData.app.grok_model_name" type="text" class="control input" />
                </div>
              </div>

              <!-- Qwen -->
              <div v-if="configData.app.llm_provider === 'qwen'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('Qwen API Key') }}</label>
                  <input v-model="configData.app.qwen_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Qwen Model Name') }}</label>
                  <input v-model="configData.app.qwen_model_name" type="text" class="control input" />
                </div>
              </div>

              <!-- MiniMax -->
              <div v-if="configData.app.llm_provider === 'minimax'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('MiniMax API Key') }}</label>
                  <input v-model="configData.app.minimax_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('MiniMax Base URL') }}</label>
                  <input v-model="configData.app.minimax_base_url" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('MiniMax Model Name') }}</label>
                  <input v-model="configData.app.minimax_model_name" type="text" class="control input" />
                </div>
              </div>

              <!-- MiMo -->
              <div v-if="configData.app.llm_provider === 'mimo'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('MiMo API Key') }}</label>
                  <input v-model="configData.app.mimo_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('MiMo Base URL') }}</label>
                  <input v-model="configData.app.mimo_base_url" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('MiMo Model Name') }}</label>
                  <input v-model="configData.app.mimo_model_name" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('MiMo TTS Model Name') }}</label>
                  <input v-model="configData.app.mimo_tts_model_name" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('MiMo TTS Style Prompt') }}</label>
                  <textarea v-model="configData.app.mimo_tts_style_prompt" class="control textarea" rows="2"></textarea>
                </div>
              </div>

              <!-- OneAPI -->
              <div v-if="configData.app.llm_provider === 'oneapi'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('OneAPI API Key') }}</label>
                  <input v-model="configData.app.oneapi_api_key" type="password" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('OneAPI Base URL') }}</label>
                  <input v-model="configData.app.oneapi_base_url" type="text" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('OneAPI Model Name') }}</label>
                  <input v-model="configData.app.oneapi_model_name" type="text" class="control input" />
                </div>
              </div>

              <!-- LiteLLM -->
              <div v-if="configData.app.llm_provider === 'litellm'" class="provider-fields">
                <div class="field">
                  <label class="field-label">{{ tr('LiteLLM Model Name') }}</label>
                  <input v-model="configData.app.litellm_model_name" type="text" class="control input" />
                </div>
              </div>
            </div>

            <!-- Material Keys -->
            <div v-else-if="activeSettingsTab === 'materials'" class="settings-section-panel">
              <h2 class="settings-panel-title">{{ tr('Material Provider API Keys') }}</h2>
              <p class="settings-panel-desc">{{ tr('API keys used to download video clips from Pexels, Pixabay, Coverr, and Vecteezy.') }}</p>
              
              <div class="field">
                <label class="field-label">{{ tr('Pexels API Keys') }} ({{ tr('comma-separated') }})</label>
                <input v-model="pexelsKeysString" type="text" class="control input" placeholder="key1, key2" />
              </div>
              
              <div class="field">
                <label class="field-label">{{ tr('Pixabay API Keys') }} ({{ tr('comma-separated') }})</label>
                <input v-model="pixabayKeysString" type="text" class="control input" placeholder="key1, key2" />
              </div>
              
              <div class="field">
                <label class="field-label">{{ tr('Coverr API Keys') }} ({{ tr('comma-separated') }})</label>
                <input v-model="coverrKeysString" type="text" class="control input" placeholder="key1, key2" />
              </div>

              <div class="field">
                <label class="field-label">{{ tr('Vecteezy API Keys') }} ({{ tr('comma-separated') }})</label>
                <input v-model="vecteezyKeysString" type="text" class="control input" placeholder="key1, key2" />
              </div>

              <div class="field">
                <label class="field-label">{{ tr('Vecteezy Account ID') }}</label>
                <input v-model="configData.app.vecteezy_account_id" type="text" class="control input" placeholder="123456" />
              </div>
            </div>

            <!-- Integrations Settings -->
            <div v-else-if="activeSettingsTab === 'integrations'" class="settings-section-panel">
              <h2 class="settings-panel-title">{{ tr('Integrations') }}</h2>
              
              <!-- YouTube -->
              <div class="sub-section">
                <h3 class="sub-section-title">
                  {{ tr('YouTube Upload') }}
                  <label class="toggle-wrap">
                    <input type="checkbox" v-model="configData.youtube.enabled" class="toggle-input" />
                    <span class="toggle-track"><span class="toggle-thumb"></span></span>
                  </label>
                </h3>
                <div v-if="configData.youtube.enabled" class="sub-section-fields">
                  <div class="field-group">
                    <div class="field">
                      <label class="field-label">{{ tr('Privacy Status') }}</label>
                      <select v-model="configData.youtube.privacy_status" class="control select">
                        <option value="public">{{ tr('Public') }}</option>
                        <option value="unlisted">{{ tr('Unlisted') }}</option>
                        <option value="private">{{ tr('Private') }}</option>
                      </select>
                    </div>
                    <div class="field">
                      <label class="field-label">{{ tr('Category ID') }}</label>
                      <input v-model="configData.youtube.category_id" type="text" class="control input" placeholder="24" />
                    </div>
                  </div>
                  <div class="field">
                    <label class="field-label">{{ tr('Tags') }} ({{ tr('comma-separated') }})</label>
                    <input v-model="youtubeTagsString" type="text" class="control input" placeholder="shorts, viral" />
                  </div>
                  <label class="checkbox-wrap">
                    <input type="checkbox" v-model="configData.youtube.auto_upload" />
                    <span>{{ tr('Auto upload generated videos') }}</span>
                  </label>
                </div>
              </div>

              <!-- Facebook -->
              <div class="sub-section">
                <h3 class="sub-section-title">
                  {{ tr('Facebook Page Upload') }}
                  <label class="toggle-wrap">
                    <input type="checkbox" v-model="configData.facebook.enabled" class="toggle-input" />
                    <span class="toggle-track"><span class="toggle-thumb"></span></span>
                  </label>
                </h3>
                <div v-if="configData.facebook.enabled" class="sub-section-fields">
                  <div class="field">
                    <label class="field-label">{{ tr('Page ID') }}</label>
                    <input v-model="configData.facebook.page_id" type="text" class="control input" />
                  </div>
                  <div class="field">
                    <label class="field-label">{{ tr('Page Access Token') }}</label>
                    <input v-model="configData.facebook.access_token" type="password" class="control input" />
                  </div>
                  <label class="checkbox-wrap">
                    <input type="checkbox" v-model="configData.facebook.auto_upload" />
                    <span>{{ tr('Auto upload generated videos') }}</span>
                  </label>
                </div>
              </div>

              <!-- Discord -->
              <div class="sub-section">
                <h3 class="sub-section-title">
                  {{ tr('Discord Bot Notification') }}
                  <label class="toggle-wrap">
                    <input type="checkbox" v-model="configData.discord.enabled" class="toggle-input" />
                    <span class="toggle-track"><span class="toggle-thumb"></span></span>
                  </label>
                </h3>
                <div v-if="configData.discord.enabled" class="sub-section-fields">
                  <div class="field">
                    <label class="field-label">{{ tr('Bot Token') }}</label>
                    <input v-model="configData.discord.bot_token" type="password" class="control input" />
                  </div>
                  <div class="field">
                    <label class="field-label">{{ tr('Channel ID') }}</label>
                    <input v-model="configData.discord.channel_id" type="text" class="control input" />
                  </div>
                </div>
              </div>
            </div>

            <!-- System Settings -->
            <div v-else-if="activeSettingsTab === 'system'" class="settings-section-panel">
              <h2 class="settings-panel-title">{{ tr('System Settings') }}</h2>
              
              <div class="field">
                <label class="field-label">{{ tr('Default Subtitle Provider') }}</label>
                <select v-model="configData.app.subtitle_provider" class="control select">
                  <option value="whisper">{{ tr('Whisper (Local)') }}</option>
                  <option value="assemblyai">{{ tr('AssemblyAI (Cloud)') }}</option>
                </select>
              </div>

              <div class="field-group">
                <div class="field">
                  <label class="field-label">{{ tr('Max Concurrent Tasks') }}</label>
                  <input v-model.number="configData.app.max_concurrent_tasks" type="number" class="control input" />
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Max Queued Tasks') }}</label>
                  <input v-model.number="configData.app.max_queued_tasks" type="number" class="control input" />
                </div>
              </div>

              <div class="field-group">
                <div class="field">
                  <label class="field-label">{{ tr('Video Codec') }}</label>
                  <select v-model="configData.app.video_codec" class="control select">
                    <option value="libx264">libx264 (CPU)</option>
                    <option value="h264_nvenc">NVIDIA NVENC (h264_nvenc)</option>
                    <option value="h264_amf">AMD AMF (h264_amf)</option>
                    <option value="h264_qsv">Intel QSV (h264_qsv)</option>
                    <option value="h264_mf">Windows MediaFoundation (h264_mf)</option>
                    <option value="h264_videotoolbox">macOS VideoToolbox (h264_videotoolbox)</option>
                  </select>
                </div>
                <div class="field">
                  <label class="field-label">{{ tr('Edge TTS Timeout (seconds)') }}</label>
                  <input v-model.number="configData.app.edge_tts_timeout" type="number" class="control input" />
                </div>
              </div>

              <div class="field">
                <label class="field-label">{{ tr('BGM / Material Directory') }}</label>
                <input v-model="configData.app.material_directory" type="text" class="control input" placeholder="Path to assets folder" />
              </div>

              <div class="field">
                <label class="field-label">{{ tr('ElevenLabs API Key') }}</label>
                <input v-model="configData.elevenlabs.api_key" type="password" class="control input" placeholder="ElevenLabs API Key" />
              </div>

              <div class="field" style="margin-top:var(--sp-4)">
                <label class="field-label">{{ tr('Default Intro Video Path') }}</label>
                <div class="file-uploader">
                  <input
                    type="file"
                    accept="video/*"
                    @change="onGlobalIntroFileChange"
                    ref="globalIntroFileInput"
                    class="file-input"
                  />
                  <div class="file-uploader-content">
                    <span v-if="uploadingGlobalIntro" class="spinner"></span>
                    <span v-else-if="configData.app.intro_video_path" class="file-uploaded-name">
                      {{ globalIntroFileName || configData.app.intro_video_path.split(/[/\\]/).pop() || tr('Intro video uploaded') }}
                      <button class="btn-remove-file" @click.stop="removeGlobalIntroFile">&times;</button>
                    </span>
                    <span v-else class="file-uploader-placeholder">{{ tr('Click to upload global intro video') }}</span>
                  </div>
                </div>
              </div>

              <label class="checkbox-wrap">
                <input type="checkbox" v-model="configData.app.match_materials_to_script" />
                <span>{{ tr('Match materials to script order by default') }}</span>
              </label>

              <div class="divider"></div>

              <h3 class="sub-section-title">{{ tr('Redis Cache Status') }}</h3>
              <label class="checkbox-wrap">
                <input type="checkbox" v-model="configData.app.enable_redis" />
                <span>{{ tr('Enable Redis State Storage') }}</span>
              </label>
              
              <div v-if="configData.app.enable_redis" class="sub-section-fields">
                <div class="field-group">
                  <div class="field">
                    <label class="field-label">{{ tr('Redis Host') }}</label>
                    <input v-model="configData.app.redis_host" type="text" class="control input" />
                  </div>
                  <div class="field">
                    <label class="field-label">{{ tr('Redis Port') }}</label>
                    <input v-model.number="configData.app.redis_port" type="number" class="control input" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Save CTA -->
            <div class="settings-actions">
              <button class="btn-generate" :disabled="savingConfig" @click="saveConfig">
                <span v-if="savingConfig" class="spinner"></span>
                <template v-else>{{ tr('Save Settings') }}</template>
              </button>
              <span v-if="saveSuccessMessage" class="save-success-msg">{{ saveSuccessMessage }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- YouTube Stats Tab -->
      <div v-else-if="activeTab === 'youtube'" class="content">
        <div v-if="loadingYoutubeStatus" class="loading-state">
          <span class="spinner"></span>
          <span class="loading-text">{{ tr('Loading YouTube channel status...') }}</span>
        </div>
        
        <template v-else>
          <!-- Configuration warning if success is false -->
          <div v-if="youtubeStatus && !youtubeStatus.success" class="empty-state" style="padding: var(--sp-8) var(--sp-4);">
            <div class="empty-icon" style="color: var(--danger);">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <h3 class="empty-title">{{ tr('YouTube Integration Not Connected') }}</h3>
            <p class="empty-desc" style="max-width: 480px; margin: var(--sp-2) auto var(--sp-6);">
              {{ youtubeStatus.error || tr('Please verify your YouTube configuration in settings and complete the authorization flow.') }}
            </p>
            <button class="btn-hero" @click="activeTab = 'settings'; activeSettingsTab = 'integrations'">
              {{ tr('Configure YouTube Settings') }}
            </button>
          </div>

          <!-- YouTube Dashboard -->
          <div v-else-if="youtubeStatus && youtubeStatus.success" class="youtube-dashboard">
            <!-- Channel Header Card -->
            <div class="channel-card">
              <div class="channel-profile">
                <img 
                  v-if="youtubeStatus.thumbnails?.default?.url" 
                  :src="youtubeStatus.thumbnails.default.url" 
                  class="channel-avatar" 
                  alt="Avatar"
                />
                <div v-else class="channel-avatar-placeholder">
                  {{ youtubeStatus.title?.slice(0, 1).toUpperCase() }}
                </div>
                <div class="channel-meta">
                  <h2 class="channel-title">{{ youtubeStatus.title }}</h2>
                  <p class="channel-handle" v-if="youtubeStatus.customUrl">{{ youtubeStatus.customUrl }}</p>
                </div>
              </div>

              <!-- Mini Stats Grid -->
              <div class="channel-stats-row">
                <div class="channel-stat-item">
                  <span class="stat-num">{{ formatNumber(youtubeStatus.subscriberCount) }}</span>
                  <span class="stat-label">{{ tr('Subscribers') }}</span>
                </div>
                <div class="channel-stat-item">
                  <span class="stat-num">{{ formatNumber(youtubeStatus.viewCount) }}</span>
                  <span class="stat-label">{{ tr('Total Views') }}</span>
                </div>
                <div class="channel-stat-item">
                  <span class="stat-num">{{ formatNumber(youtubeStatus.videoCount) }}</span>
                  <span class="stat-label">{{ tr('Videos') }}</span>
                </div>
              </div>
            </div>

            <!-- YouTube Tab switcher -->
            <div class="youtube-subtabs">
              <button 
                class="subtab-btn" 
                :class="{ active: activeYoutubeSubTab === 'my-videos' }" 
                @click="activeYoutubeSubTab = 'my-videos'"
              >
                {{ tr('My Uploads') }}
              </button>
              <button 
                class="subtab-btn" 
                :class="{ active: activeYoutubeSubTab === 'trends' }" 
                @click="activeYoutubeSubTab = 'trends'"
              >
                {{ tr('YouTube Trends') }}
              </button>
              <button 
                class="subtab-btn" 
                :class="{ active: activeYoutubeSubTab === 'search' }" 
                @click="activeYoutubeSubTab = 'search'"
              >
                {{ tr('Lookup Video') }}
              </button>
            </div>

            <!-- Subtab Content: My Uploads -->
            <div v-if="activeYoutubeSubTab === 'my-videos'" class="subtab-content">
              <div v-if="loadingYoutubeVideos" class="loading-state" style="padding: var(--sp-6) 0;">
                <span class="spinner"></span>
                <span class="loading-text">{{ tr('Loading uploaded videos...') }}</span>
              </div>
              <div v-else-if="youtubeVideos.length === 0" class="empty-state" style="padding: var(--sp-6) 0;">
                <p class="empty-desc">{{ tr('No recent video uploads found.') }}</p>
              </div>
              <div v-else class="my-videos-analytics">
                <!-- Analytics Section -->
                <div class="analytics-section">
                  <!-- Chart Card -->
                  <div class="chart-card">
                    <div class="chart-header">
                      <h3 class="chart-title">{{ tr('Upload Performance Trend') }}</h3>
                      <div class="metric-selector">
                        <button 
                          v-for="m in ['views', 'likes', 'comments']" 
                          :key="m"
                          class="metric-btn"
                          :class="{ active: selectedChartMetric === m }"
                          @click="selectedChartMetric = m"
                        >
                          {{ tr(m.charAt(0).toUpperCase() + m.slice(1)) }}
                        </button>
                      </div>
                    </div>
                    
                    <!-- Interactive SVG Chart -->
                    <div class="svg-chart-container">
                      <svg 
                        width="100%" 
                        height="220" 
                        viewBox="0 0 600 220" 
                        preserveAspectRatio="none"
                        class="trend-svg"
                        @mouseleave="hoveredPoint = null"
                      >
                        <!-- Grid lines -->
                        <line x1="35" y1="30" x2="565" y2="30" stroke="var(--edge)" stroke-dasharray="4,4" />
                        <line x1="35" y1="75" x2="565" y2="75" stroke="var(--edge)" stroke-dasharray="4,4" />
                        <line x1="35" y1="120" x2="565" y2="120" stroke="var(--edge)" stroke-dasharray="4,4" />
                        <line x1="35" y1="165" x2="565" y2="165" stroke="var(--edge)" stroke-dasharray="4,4" />
                        
                        <!-- Area under path with gradient -->
                        <path 
                          v-if="chartPaths.areaPath"
                          :d="chartPaths.areaPath" 
                          fill="url(#chartGradient)" 
                          opacity="0.15" 
                        />
                        
                        <!-- Line path -->
                        <path 
                          v-if="chartPaths.linePath"
                          :d="chartPaths.linePath" 
                          fill="none" 
                          stroke="var(--brand)" 
                          stroke-width="3" 
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                        
                        <!-- Interactive Points -->
                        <circle 
                          v-for="(pt, idx) in chartPoints" 
                          :key="idx"
                          :cx="pt.x" 
                          :cy="pt.y" 
                          r="6" 
                          :fill="hoveredPoint?.index === idx ? 'var(--brand-hover)' : 'var(--brand)'"
                          stroke="var(--surface-1)"
                          stroke-width="2"
                          class="chart-node"
                          @mouseenter="hoveredPoint = { index: idx, ...pt }"
                        />
                        
                        <!-- Definitions for gradient -->
                        <defs>
                          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="var(--brand)" />
                            <stop offset="100%" stop-color="var(--brand)" stop-opacity="0" />
                          </linearGradient>
                        </defs>
                      </svg>
                    </div>
                    
                    <!-- Tooltip info display inside the card -->
                    <div class="chart-tooltip-display" v-if="hoveredPoint">
                      <img 
                        v-if="hoveredPoint.video.thumbnails?.default?.url"
                        :src="hoveredPoint.video.thumbnails.default.url" 
                        class="tooltip-thumb"
                      />
                      <div class="tooltip-info">
                        <p class="tooltip-title">{{ hoveredPoint.video.title }}</p>
                        <p class="tooltip-meta">
                          <span>{{ formatDate(hoveredPoint.video.publishedAt) }}</span>
                          <span class="tooltip-value">
                            <strong>{{ formatNumber(hoveredPoint.value) }}</strong> {{ tr(selectedChartMetric) }}
                          </span>
                        </p>
                      </div>
                    </div>
                    <div v-else class="chart-tooltip-placeholder">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: var(--sp-1);">
                        <circle cx="12" cy="12" r="10" />
                        <path d="M12 16v-4M12 8h.01" />
                      </svg>
                      <span>{{ tr('Hover over points on the chart to see video details.') }}</span>
                    </div>
                  </div>

                  <!-- Insights Card -->
                  <div class="insights-card">
                    <h3 class="insights-title">{{ tr('Performance Insights') }}</h3>
                    
                    <div class="insights-row">
                      <div class="insight-metric">
                        <span class="insight-label">{{ tr('Top Video') }}</span>
                        <span class="insight-value text-ellipsis" :title="topPerformingVideo?.title || '-'">
                          {{ topPerformingVideo ? truncateText(topPerformingVideo.title, 25) : '-' }}
                        </span>
                        <span class="insight-sub" v-if="topPerformingVideo">
                          {{ formatNumber(topPerformingVideo.viewCount) }} {{ tr('views') }}
                        </span>
                      </div>
                      
                      <div class="insight-metric">
                        <span class="insight-label">{{ tr('Avg. Engagement') }}</span>
                        <span class="insight-value">{{ averageEngagementRate }}%</span>
                        <span class="insight-sub">{{ tr('Likes + comments per view') }}</span>
                      </div>
                    </div>
                    
                    <!-- Dynamic Explanation -->
                    <div class="explanation-box">
                      <div class="explanation-icon">💡</div>
                      <div class="explanation-text">
                        <p class="explanation-header">{{ tr('How to Read the Chart') }}</p>
                        <p class="explanation-desc">{{ getChartInterpretation() }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Recent Uploads grid list -->
                <div class="list-section-header" style="margin: var(--sp-6) 0 var(--sp-3); border-bottom: 1px solid var(--edge); padding-bottom: var(--sp-2);">
                  <h3 style="font-size: var(--sp-4); font-weight: 700; color: var(--ink-primary);">{{ tr('Recent Uploads') }}</h3>
                </div>
                <div class="youtube-videos-grid">
                  <div v-for="video in youtubeVideos" :key="video.id" class="yt-video-card">
                    <div class="yt-thumb-wrap">
                      <img :src="video.thumbnails?.medium?.url" class="yt-thumb" alt="Thumbnail" />
                      <span v-if="video.privacyStatus" class="yt-status-badge" :class="[video.privacyStatus, video.publishAt ? 'scheduled' : '']">
                        {{ getPrivacyStatusLabel(video) }}
                      </span>
                      <a :href="'https://youtube.com/watch?v=' + video.id" target="_blank" class="yt-play-btn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                          <polygon points="5 3 19 12 5 21 5 3"></polygon>
                        </svg>
                      </a>
                    </div>
                    <div class="yt-card-body">
                      <h4 class="yt-video-title" :title="video.title">{{ video.title }}</h4>
                      <p class="yt-video-date">{{ formatDate(video.publishedAt) }}</p>
                      
                      <div class="yt-video-stats">
                        <div class="yt-stat" :title="tr('Views')">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                          <span>{{ formatNumber(video.viewCount) }}</span>
                        </div>
                        <div class="yt-stat" :title="tr('Likes')">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                          </svg>
                          <span>{{ formatNumber(video.likeCount) }}</span>
                        </div>
                        <div class="yt-stat" :title="tr('Comments')">
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                          </svg>
                          <span>{{ formatNumber(video.commentCount) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Subtab Content: YouTube Trends -->
            <div v-else-if="activeYoutubeSubTab === 'trends'" class="subtab-content">
              <div class="trends-header">
                <div class="field" style="margin-bottom: 0; display: flex; align-items: center; gap: var(--sp-3);">
                  <label class="field-label" style="margin-bottom: 0; font-weight: 500;">{{ tr('Trending Region') }}</label>
                  <select 
                    v-model="selectedTrendsRegion" 
                    class="control select" 
                    style="width: 160px;" 
                    @change="loadYoutubeTrends"
                  >
                    <option v-for="r in regions" :key="r.code" :value="r.code">{{ r.name }}</option>
                  </select>
                </div>
              </div>

              <div v-if="loadingYoutubeTrends" class="loading-state" style="padding: var(--sp-6) 0;">
                <span class="spinner"></span>
                <span class="loading-text">{{ tr('Loading trending videos...') }}</span>
              </div>
              <div v-else-if="youtubeTrends.length === 0" class="empty-state" style="padding: var(--sp-6) 0;">
                <p class="empty-desc">{{ tr('No trending videos found.') }}</p>
              </div>
              <div v-else class="youtube-videos-grid">
                <div v-for="video in youtubeTrends" :key="video.id" class="yt-video-card">
                  <div class="yt-thumb-wrap">
                    <img :src="video.thumbnails?.medium?.url" class="yt-thumb" alt="Thumbnail" />
                    <a :href="'https://youtube.com/watch?v=' + video.id" target="_blank" class="yt-play-btn">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                    </a>
                  </div>
                  <div class="yt-card-body">
                    <h4 class="yt-video-title" :title="video.title">{{ video.title }}</h4>
                    <p class="yt-video-channel">{{ video.channelTitle }}</p>
                    <p class="yt-video-date">{{ formatDate(video.publishedAt) }}</p>
                    
                    <div class="yt-video-stats">
                      <div class="yt-stat" :title="tr('Views')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                        <span>{{ formatNumber(video.viewCount) }}</span>
                      </div>
                      <div class="yt-stat" :title="tr('Likes')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                        </svg>
                        <span>{{ formatNumber(video.likeCount) }}</span>
                      </div>
                      <div class="yt-stat" :title="tr('Comments')">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                        </svg>
                        <span>{{ formatNumber(video.commentCount) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Subtab Content: Lookup Video -->
            <div v-else-if="activeYoutubeSubTab === 'search'" class="subtab-content">
              <div class="search-bar-wrap">
                <div class="hero-field">
                  <input
                    v-model="searchVideoQuery"
                    type="text"
                    class="hero-text"
                    :placeholder="tr('Enter YouTube Video URL or Video ID (e.g. https://www.youtube.com/watch?v=...)')"
                    @keyup.enter="searchYoutubeVideo"
                  />
                  <button 
                    class="btn-hero" 
                    :disabled="loadingSearchVideo || !searchVideoQuery" 
                    @click="searchYoutubeVideo"
                  >
                    <span v-if="loadingSearchVideo" class="spinner"></span>
                    <template v-else>{{ tr('Lookup') }}</template>
                  </button>
                </div>
              </div>

              <!-- Search Error -->
              <div v-if="searchError" class="search-error-box">
                {{ searchError }}
              </div>

              <!-- Searched Video Card Details -->
              <div v-if="searchedVideoResult" class="searched-video-result">
                <div class="yt-video-card detail-view">
                  <div class="yt-thumb-wrap">
                    <img :src="searchedVideoResult.thumbnails?.high?.url || searchedVideoResult.thumbnails?.medium?.url" class="yt-thumb" alt="Thumbnail" />
                    <span v-if="searchedVideoResult.privacyStatus" class="yt-status-badge" :class="[searchedVideoResult.privacyStatus, searchedVideoResult.publishAt ? 'scheduled' : '']">
                      {{ getPrivacyStatusLabel(searchedVideoResult) }}
                    </span>
                    <a :href="'https://youtube.com/watch?v=' + searchedVideoResult.id" target="_blank" class="yt-play-btn large">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                      </svg>
                    </a>
                  </div>
                  <div class="yt-card-body">
                    <h3 class="yt-video-title-large">{{ searchedVideoResult.title }}</h3>
                    <p class="yt-video-channel" style="font-size: var(--sp-4);">{{ searchedVideoResult.channelTitle }}</p>
                    <p class="yt-video-date">{{ formatDate(searchedVideoResult.publishedAt) }}</p>
                    
                    <div class="yt-video-stats large-stats">
                      <div class="yt-stat-large">
                        <span class="stat-icon">👁️</span>
                        <div class="stat-text">
                          <span class="stat-value">{{ formatNumber(searchedVideoResult.viewCount) }}</span>
                          <span class="stat-name">{{ tr('Views') }}</span>
                        </div>
                      </div>
                      <div class="yt-stat-large">
                        <span class="stat-icon">👍</span>
                        <div class="stat-text">
                          <span class="stat-value">{{ formatNumber(searchedVideoResult.likeCount) }}</span>
                          <span class="stat-name">{{ tr('Likes') }}</span>
                        </div>
                      </div>
                      <div class="yt-stat-large">
                        <span class="stat-icon">💬</span>
                        <div class="stat-text">
                          <span class="stat-value">{{ formatNumber(searchedVideoResult.commentCount) }}</span>
                          <span class="stat-name">{{ tr('Comments') }}</span>
                        </div>
                      </div>
                    </div>

                    <div v-if="searchedVideoResult.description" class="yt-video-desc-box">
                      <p class="desc-title">{{ tr('Description') }}</p>
                      <pre class="desc-text">{{ searchedVideoResult.description }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>

    <!-- Modal for Logs -->
    <div v-if="showLogModal" class="modal-overlay" @click.self="showLogModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">{{ tr('Task Logs') }} ({{ logModalTaskId?.slice(0, 8) }})</h3>
          <button class="modal-close" @click="showLogModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="terminal">
            <pre>{{ modalLogText }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'
import { useI18n } from '~/composables/useI18n'

const api = useApi()
const { tr, setLocale, loadLocales, getLocaleList } = useI18n()

const locale = ref('en')
const localeList = ref<{ code: string; name: string }[]>([])
const generating = ref(false)
const isGenerating = ref(false)
const voices = ref<{ id: string; name: string }[]>([])
const fonts = ref<string[]>([])
const activeTask = ref<any>(null)
const taskLog = ref('')
const activeTab = ref<'create' | 'tasks' | 'settings' | 'youtube'>('create')

// YouTube stats & trends state
const activeYoutubeSubTab = ref<'my-videos' | 'trends' | 'search'>('my-videos')
const youtubeStatus = ref<any>(null)
const loadingYoutubeStatus = ref(false)
const youtubeVideos = ref<any[]>([])
const loadingYoutubeVideos = ref(false)
const youtubeTrends = ref<any[]>([])
const loadingYoutubeTrends = ref(false)
const selectedTrendsRegion = ref('US')
const searchVideoQuery = ref('')
const searchedVideoResult = ref<any>(null)
const loadingSearchVideo = ref(false)
const searchError = ref('')

const selectedChartMetric = ref<'views' | 'likes' | 'comments'>('views')
const hoveredPoint = ref<any>(null)

const chartPoints = computed(() => {
  if (!youtubeVideos.value || youtubeVideos.value.length === 0) return []
  const vids = [...youtubeVideos.value].reverse()
  const metric = selectedChartMetric.value
  
  const values = vids.map(v => {
    const valStr = metric === 'views' ? v.viewCount : (metric === 'likes' ? v.likeCount : v.commentCount)
    return parseInt(valStr, 10) || 0
  })
  
  const maxVal = Math.max(...values, 1)
  const minVal = 0
  const range = maxVal - minVal
  
  const width = 600
  const height = 220
  const paddingLeft = 35
  const paddingRight = 35
  const paddingTop = 30
  const paddingBottom = 40
  
  const usableWidth = width - paddingLeft - paddingRight
  const usableHeight = height - paddingTop - paddingBottom
  
  return vids.map((video, idx) => {
    const val = values[idx]
    const x = vids.length > 1 
      ? paddingLeft + (idx * usableWidth) / (vids.length - 1)
      : width / 2
    const y = height - paddingBottom - ((val - minVal) / range) * usableHeight
    return {
      x,
      y,
      value: val,
      video
    }
  })
})

const chartPaths = computed(() => {
  const pts = chartPoints.value
  if (pts.length === 0) {
    return { linePath: '', areaPath: '' }
  }
  
  let linePath = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    linePath += ` L ${pts[i].x} ${pts[i].y}`
  }
  
  const startX = pts[0].x
  const endX = pts[pts.length - 1].x
  const bottomY = 180
  
  const areaPath = `${linePath} L ${endX} ${bottomY} L ${startX} ${bottomY} Z`
  
  return { linePath, areaPath }
})

const topPerformingVideo = computed(() => {
  if (!youtubeVideos.value || youtubeVideos.value.length === 0) return null
  return [...youtubeVideos.value].reduce((prev, current) => {
    const prevViews = parseInt(prev.viewCount, 10) || 0
    const currViews = parseInt(current.viewCount, 10) || 0
    return currViews > prevViews ? current : prev
  })
})

const averageEngagementRate = computed(() => {
  if (!youtubeVideos.value || youtubeVideos.value.length === 0) return '0.0'
  let totalViews = 0
  let totalEngagement = 0
  youtubeVideos.value.forEach(v => {
    const views = parseInt(v.viewCount, 10) || 0
    const likes = parseInt(v.likeCount, 10) || 0
    const comments = parseInt(v.commentCount, 10) || 0
    totalViews += views
    totalEngagement += (likes + comments)
  })
  if (totalViews === 0) return '0.0'
  return ((totalEngagement / totalViews) * 100).toFixed(1)
})

function getChartInterpretation(): string {
  const isIndonesian = locale.value === 'id'
  if (!youtubeVideos.value || youtubeVideos.value.length === 0) {
    return isIndonesian 
      ? 'Belum ada data untuk ditampilkan. Unggah video terlebih dahulu.'
      : 'No data to display. Please upload videos first.'
  }
  
  const metric = selectedChartMetric.value
  const pts = chartPoints.value
  if (pts.length < 2) {
    return isIndonesian
      ? 'Grafik memerlukan minimal 2 video untuk menunjukkan tren.'
      : 'The chart requires at least 2 videos to show a trend.'
  }
  
  const lastVal = pts[pts.length - 1].value
  const avgVal = pts.reduce((sum, pt) => sum + pt.value, 0) / pts.length
  
  let trendDirection = ''
  if (lastVal > avgVal * 1.15) {
    trendDirection = isIndonesian 
      ? 'meningkat pesat dibanding rata-rata' 
      : 'increased significantly compared to the average'
  } else if (lastVal < avgVal * 0.85) {
    trendDirection = isIndonesian
      ? 'menurun dari rata-rata'
      : 'decreased below the average'
  } else {
    trendDirection = isIndonesian
      ? 'stabil mendekati rata-rata'
      : 'stable close to the average'
  }
  
  const metricName = isIndonesian 
    ? (metric === 'views' ? 'penayangan' : (metric === 'likes' ? 'suka' : 'komentar'))
    : (metric === 'views' ? 'views' : (metric === 'likes' ? 'likes' : 'comments'))
  
  return isIndonesian
    ? `Grafik menunjukkan performa video Anda berdasarkan urutan rilis (kiri = terlama, kanan = terbaru). Saat ini, tren ${metricName} untuk video terbaru Anda terpantau ${trendDirection}. Arahkan kursor ke titik grafik untuk info detail.`
    : `The chart displays video performance chronologically (left = oldest, right = newest). Currently, the ${metricName} trend for your latest video is ${trendDirection}. Hover over any point to inspect individual video statistics.`
}


const regions = [
  { code: 'US', name: 'United States' },
  { code: 'ID', name: 'Indonesia' },
  { code: 'IN', name: 'India' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'BR', name: 'Brazil' },
  { code: 'JP', name: 'Japan' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'KR', name: 'South Korea' }
]

async function loadYoutubeStatus() {
  loadingYoutubeStatus.value = true
  try {
    const res = await api.getYoutubeStatus()
    if (res && res.data) {
      youtubeStatus.value = res.data
    } else {
      youtubeStatus.value = { success: false, error: 'Failed to retrieve channel status' }
    }
  } catch (err: any) {
    youtubeStatus.value = { success: false, error: err.message || 'Connection error' }
  } finally {
    loadingYoutubeStatus.value = false
  }
}

async function loadYoutubeVideos() {
  loadingYoutubeVideos.value = true
  try {
    const res = await api.getYoutubeVideos(20)
    if (res && res.data && res.data.success) {
      youtubeVideos.value = res.data.videos || []
    } else {
      youtubeVideos.value = []
    }
  } catch (err) {
    youtubeVideos.value = []
  } finally {
    loadingYoutubeVideos.value = false
  }
}

async function loadYoutubeTrends() {
  loadingYoutubeTrends.value = true
  try {
    const res = await api.getYoutubeTrends(selectedTrendsRegion.value, 15)
    if (res && res.data && res.data.success) {
      youtubeTrends.value = res.data.videos || []
    } else {
      youtubeTrends.value = []
    }
  } catch (err) {
    youtubeTrends.value = []
  } finally {
    loadingYoutubeTrends.value = false
  }
}

function extractYoutubeVideoId(urlOrId: string): string | null {
  const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/
  const match = urlOrId.match(regExp)
  if (match && match[2].length === 11) {
    return match[2]
  }
  const cleanId = urlOrId.trim()
  if (cleanId.length === 11) {
    return cleanId
  }
  return null
}

async function searchYoutubeVideo() {
  searchError.value = ''
  searchedVideoResult.value = null
  const videoId = extractYoutubeVideoId(searchVideoQuery.value)
  if (!videoId) {
    searchError.value = tr('Invalid YouTube Video URL or Video ID')
    return
  }
  loadingSearchVideo.value = true
  try {
    const res = await api.getYoutubeVideoStats(videoId)
    if (res && res.data && res.data.success) {
      searchedVideoResult.value = res.data.video
    } else {
      searchError.value = res?.data?.error || tr('Video not found or is private')
    }
  } catch (err: any) {
    searchError.value = err.message || tr('Error fetching video statistics')
  } finally {
    loadingSearchVideo.value = false
  }
}

async function loadYoutubeData() {
  await loadYoutubeStatus()
  if (youtubeStatus.value && youtubeStatus.value.success) {
    if (activeYoutubeSubTab.value === 'my-videos') {
      await loadYoutubeVideos()
    } else if (activeYoutubeSubTab.value === 'trends') {
      await loadYoutubeTrends()
    }
  }
}

function formatNumber(num: any): string {
  if (num === undefined || num === null) return '0'
  const val = typeof num === 'string' ? parseInt(num, 10) : num
  if (isNaN(val)) return '0'
  if (val >= 1000000) {
    return (val / 1000000).toFixed(1) + 'M'
  }
  if (val >= 1000) {
    return (val / 1000).toFixed(1) + 'K'
  }
  return val.toString()
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function getPrivacyStatusLabel(video: any): string {
  if (video.publishAt) {
    return tr('Scheduled')
  }
  if (video.privacyStatus === 'public') {
    return tr('Published')
  }
  if (video.privacyStatus === 'private') {
    return tr('Private')
  }
  if (video.privacyStatus === 'unlisted') {
    return tr('Unlisted')
  }
  return video.privacyStatus || ''
}

// Tasks tab state
const tasks = ref<any[]>([])
const loadingTasks = ref(false)
const showLogModal = ref(false)
const logModalTaskId = ref('')
const modalLogText = ref('')

// Settings tab state
const activeSettingsTab = ref<'llm' | 'materials' | 'integrations' | 'system'>('llm')
const configData = ref<any>({
  app: {},
  azure: {},
  siliconflow: {},
  elevenlabs: {},
  ui: {},
  discord: {},
  youtube: {},
  facebook: {}
})
const savingConfig = ref(false)
const saveSuccessMessage = ref('')

const pexelsKeysString = computed({
  get: () => Array.isArray(configData.value.app?.pexels_api_keys) ? configData.value.app.pexels_api_keys.join(', ') : '',
  set: (val: string) => {
    if (!configData.value.app) configData.value.app = {}
    configData.value.app.pexels_api_keys = val.split(',').map((s: string) => s.trim()).filter(Boolean)
  }
})
const pixabayKeysString = computed({
  get: () => Array.isArray(configData.value.app?.pixabay_api_keys) ? configData.value.app.pixabay_api_keys.join(', ') : '',
  set: (val: string) => {
    if (!configData.value.app) configData.value.app = {}
    configData.value.app.pixabay_api_keys = val.split(',').map((s: string) => s.trim()).filter(Boolean)
  }
})
const coverrKeysString = computed({
  get: () => Array.isArray(configData.value.app?.coverr_api_keys) ? configData.value.app.coverr_api_keys.join(', ') : '',
  set: (val: string) => {
    if (!configData.value.app) configData.value.app = {}
    configData.value.app.coverr_api_keys = val.split(',').map((s: string) => s.trim()).filter(Boolean)
  }
})
const vecteezyKeysString = computed({
  get: () => Array.isArray(configData.value.app?.vecteezy_api_keys) ? configData.value.app.vecteezy_api_keys.join(', ') : '',
  set: (val: string) => {
    if (!configData.value.app) configData.value.app = {}
    configData.value.app.vecteezy_api_keys = val.split(',').map((s: string) => s.trim()).filter(Boolean)
  }
})
const youtubeTagsString = computed({
  get: () => Array.isArray(configData.value.youtube?.tags) ? configData.value.youtube.tags.join(', ') : '',
  set: (val: string) => {
    if (!configData.value.youtube) configData.value.youtube = {}
    configData.value.youtube.tags = val.split(',').map((s: string) => s.trim()).filter(Boolean)
  }
})

const supportLocales = ['zh-CN','zh-HK','zh-TW','de-DE','en-US','fr-FR','ru-RU','vi-VN','th-TH','tr-TR']

const form = ref({
  video_subject: '',
  video_script: '',
  video_terms: '',
  video_language: '',
  paragraph_number: 1,
  video_script_prompt: '',
  video_source: 'pexels',
  video_aspect: '9:16',
  video_clip_duration: 3,
  video_count: 1,
  video_concat_mode: 'random',
  video_transition_mode: null as string | null,
  tts_server: 'azure-tts-v1',
  voice_name: '',
  voice_rate: 1.0,
  voice_volume: 1.0,
  bgm_type: 'random',
  bgm_volume: 0.2,
  subtitle_enabled: true,
  font_name: '',
  subtitle_position: 'bottom',
  text_fore_color: '#FFFFFF',
  font_size: 60,
  stroke_color: '#000000',
  stroke_width: 1.5,
  publish_at: '',
})

const taskBadgeClass = computed(() => {
  if (!activeTask.value) return ''
  if (activeTask.value.state === 1) return 'badge-success'
  if (activeTask.value.state === -1) return 'badge-danger'
  return 'badge-processing'
})

const taskStatusLabel = computed(() => {
  if (!activeTask.value) return ''
  if (activeTask.value.state === 1) return tr('Complete')
  if (activeTask.value.state === -1) return tr('Failed')
  return tr('Processing')
})

const taskPctColor = computed(() => {
  if (!activeTask.value) return 'var(--ink-tertiary)'
  if (activeTask.value.state === 1) return 'var(--success)'
  if (activeTask.value.state === -1) return 'var(--danger)'
  return 'var(--brand)'
})




const globalIntroFileName = ref('')
const uploadingGlobalIntro = ref(false)
const globalIntroFileInput = ref<HTMLInputElement | null>(null)

async function onGlobalIntroFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  
  uploadingGlobalIntro.value = true
  try {
    const res = await api.uploadFile(file)
    if (res.data?.file_path) {
      if (!configData.value.app) configData.value.app = {}
      configData.value.app.intro_video_path = res.data.file_path
      globalIntroFileName.value = file.name
    }
  } catch (err) {
    alert(tr('Failed to upload global intro video.'))
  } finally {
    uploadingGlobalIntro.value = false
  }
}

function removeGlobalIntroFile() {
  if (configData.value.app) {
    configData.value.app.intro_video_path = ''
  }
  globalIntroFileName.value = ''
  if (globalIntroFileInput.value) {
    globalIntroFileInput.value.value = ''
  }
}

const previewingVoice = ref(false)
const previewAudio = ref<HTMLAudioElement | null>(null)

async function playVoicePreview() {
  if (!form.value.voice_name) return
  
  if (previewAudio.value) {
    previewAudio.value.pause()
    previewAudio.value = null
  }
  
  previewingVoice.value = true
  try {
    const previewText = form.value.video_language === 'zh-CN' || form.value.video_language === 'zh'
      ? "您好！这是所选声音的测试音频。" 
      : "Hello! This is a preview of the selected voice."
      
    const res = await fetch('/api/v1/voice/preview', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: previewText,
        voice_name: form.value.voice_name,
        voice_rate: form.value.voice_rate,
        voice_volume: form.value.voice_volume
      })
    })
    
    if (res.ok) {
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      previewAudio.value = new Audio(url)
      previewAudio.value.play()
    } else {
      alert(tr('Voice preview failed'))
    }
  } catch (err) {
    console.error(err)
    alert(tr('Voice preview error'))
  } finally {
    previewingVoice.value = false
  }
}

function onLocaleChange() { setLocale(locale.value) }

async function loadVoices() {
  const res = await api.getVoices(form.value.tts_server)
  voices.value = res.data || []
  if (voices.value.length) form.value.voice_name = voices.value[0].id
}

async function loadFonts() {
  const res = await api.getFonts()
  fonts.value = res.data || []
  if (fonts.value.length) form.value.font_name = fonts.value[0]
}

async function loadConfig() {
  try {
    const res = await api.getConfig()
    if (res.data) {
      configData.value = res.data
      const cfg = res.data
      if (cfg.ui?.language) { locale.value = cfg.ui.language; setLocale(cfg.ui.language) }
      if (cfg.ui?.voice_name) form.value.voice_name = cfg.ui.voice_name
      if (cfg.ui?.tts_server) form.value.tts_server = cfg.ui.tts_server
      if (cfg.ui?.font_name) form.value.font_name = cfg.ui.font_name
      if (cfg.ui?.subtitle_position) form.value.subtitle_position = cfg.ui.subtitle_position
      if (cfg.ui?.text_fore_color) form.value.text_fore_color = cfg.ui.text_fore_color
      if (cfg.ui?.font_size) form.value.font_size = cfg.ui.font_size
      if (cfg.app?.video_source) form.value.video_source = cfg.app.video_source
    }
  } catch { /* best-effort */ }
}

async function saveConfig() {
  savingConfig.value = true
  saveSuccessMessage.value = ''
  try {
    const res = await api.saveConfig(configData.value)
    if (res.status === 200) {
      saveSuccessMessage.value = tr('Configuration saved successfully!')
      setTimeout(() => { saveSuccessMessage.value = '' }, 3000)
    }
  } catch {
    alert(tr('Failed to save configuration.'))
  } finally {
    savingConfig.value = false
  }
}

async function generateScriptAndTerms() {
  if (!form.value.video_subject) return
  generating.value = true
  try {
    const scriptRes = await api.generateScript({
      video_subject: form.value.video_subject,
      video_language: form.value.video_language,
      paragraph_number: form.value.paragraph_number,
      video_script_prompt: form.value.video_script_prompt,
    })
    if (scriptRes.data?.video_script) form.value.video_script = scriptRes.data.video_script
    const termsRes = await api.generateTerms({
      video_subject: form.value.video_subject,
      video_script: form.value.video_script,
      amount: 5,
    })
    if (termsRes.data?.video_terms) form.value.video_terms = termsRes.data.video_terms.join(', ')
  } finally { generating.value = false }
}

async function generateVideo() {
  if (!form.value.video_subject && !form.value.video_script) return
  isGenerating.value = true
  taskLog.value = ''
  activeTask.value = null
  try {
    const res = await api.createVideo({
      video_subject: form.value.video_subject,
      video_script: form.value.video_script,
      video_terms: form.value.video_terms,
      video_language: form.value.video_language,
      video_source: form.value.video_source,
      video_aspect: form.value.video_aspect,
      video_clip_duration: form.value.video_clip_duration,
      video_count: form.value.video_count,
      video_concat_mode: form.value.video_concat_mode,
      video_transition_mode: form.value.video_transition_mode,
      voice_name: form.value.voice_name,
      voice_rate: form.value.voice_rate,
      voice_volume: form.value.voice_volume,
      bgm_type: form.value.bgm_type,
      bgm_volume: form.value.bgm_volume,
      subtitle_enabled: form.value.subtitle_enabled,
      subtitle_position: form.value.subtitle_position,
      font_name: form.value.font_name,
      text_fore_color: form.value.text_fore_color,
      font_size: form.value.font_size,
      stroke_color: form.value.stroke_color,
      stroke_width: form.value.stroke_width,
      paragraph_number: form.value.paragraph_number,
      publish_at: form.value.publish_at ? new Date(form.value.publish_at).toISOString() : null,
      intro_video_path: configData.value.app?.intro_video_path || null,
    })
    if (res.data?.task_id) {
      const taskId = res.data.task_id
      activeTask.value = { task_id: taskId, state: 1, progress: 0 }
      pollTask(taskId)
      streamLog(taskId)
    }
  } catch { isGenerating.value = false }
}

async function pollTask(taskId: string) {
  while (true) {
    await new Promise(r => setTimeout(r, 2000))
    try {
      const res = await api.getTask(taskId)
      if (res.data) {
        activeTask.value = res.data
        if (res.data.state === 1 || res.data.state === -1) { isGenerating.value = false; return }
      }
    } catch { /* ignore */ }
  }
}

async function streamLog(taskId: string) {
  for await (const chunk of api.streamTaskLog(taskId)) {
    taskLog.value += chunk
    if (activeTask.value?.state === 1 || activeTask.value?.state === -1) return
  }
}

async function loadTasks() {
  loadingTasks.value = true
  try {
    const res = await api.getTasks()
    if (res.data && res.data.tasks) {
      tasks.value = res.data.tasks
    }
  } catch {
    //
  } finally {
    loadingTasks.value = false
  }
}

function getTaskBadgeClass(state: number) {
  if (state === 1) return 'badge-success'
  if (state === -1) return 'badge-danger'
  return 'badge-processing'
}

function getTaskStatusLabel(state: number) {
  if (state === 1) return tr('Complete')
  if (state === -1) return tr('Failed')
  return tr('Processing')
}

async function viewTaskLogs(task: any) {
  showLogModal.value = true
  logModalTaskId.value = task.task_id
  modalLogText.value = ''
  
  try {
    for await (const chunk of api.streamTaskLog(task.task_id)) {
      if (!showLogModal.value || logModalTaskId.value !== task.task_id) return
      modalLogText.value += chunk
      
      const currentTask = tasks.value.find(t => t.task_id === task.task_id)
      if (currentTask && (currentTask.state === 1 || currentTask.state === -1)) {
        break
      }
    }
  } catch { /* ignore */ }
}

async function confirmDeleteTask(taskId: string) {
  if (confirm(tr('Are you sure you want to delete this task?'))) {
    try {
      await api.deleteTask(taskId)
      await loadTasks()
      if (activeTask.value && activeTask.value.task_id === taskId) {
        activeTask.value = null
      }
    } catch {
      //
    }
  }
}

function truncateText(text: string, maxLen: number) {
  if (!text) return ''
  if (text.length <= maxLen) return text
  return text.slice(0, maxLen) + '...'
}

watch(activeTab, (newTab) => {
  if (newTab === 'tasks') {
    loadTasks()
  } else if (newTab === 'youtube') {
    loadYoutubeData()
  }
})

watch(activeYoutubeSubTab, (newSubTab) => {
  if (activeTab.value === 'youtube' && youtubeStatus.value?.success) {
    if (newSubTab === 'my-videos') {
      loadYoutubeVideos()
    } else if (newSubTab === 'trends') {
      loadYoutubeTrends()
    }
  }
})

onMounted(async () => {
  await loadLocales()
  localeList.value = getLocaleList()
  await loadConfig()
  await loadVoices()
  await loadFonts()
})
</script>

<style scoped>
/* === LAYOUT: sidebar + main === */
.shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
}

@media (max-width: 860px) {
  .shell { grid-template-columns: 1fr; }
  .sidebar { display: none; } /* ponytail: mobile nav → hamburger when needed */
}

/* === SIDEBAR === */
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  background: var(--surface-1);
  border-right: 1px solid var(--edge);
  display: flex;
  flex-direction: column;
  padding: var(--sp-5);
  gap: var(--sp-6);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding-bottom: var(--sp-5);
  border-bottom: 1px solid var(--edge);
}

.brand-mark {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-muted);
  border-radius: var(--radius-sm);
}

.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--ink-primary);
  letter-spacing: -0.02em;
}

.brand-tag {
  font-size: 11px;
  font-weight: 600;
  color: var(--brand);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--sp-1);
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-3);
  border-radius: var(--radius-sm);
  border: none;
  background: none;
  color: var(--ink-secondary);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}

.nav-item:hover { background: var(--brand-subtle); color: var(--ink-primary); }
.nav-item.active { background: var(--brand-muted); color: var(--brand); }

.sidebar-footer { margin-top: auto; }

.locale-picker {
  width: 100%;
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  color: var(--ink-secondary);
  padding: var(--sp-2) var(--sp-3);
  font-size: 12px;
  font-family: inherit;
  cursor: pointer;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.locale-picker:hover { border-color: var(--control-border-hover); }
.locale-picker:focus { outline: none; border-color: var(--control-border-focus); }

/* === MAIN === */
.main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.topbar {
  padding: var(--sp-6) var(--sp-8);
  border-bottom: 1px solid var(--edge);
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--ink-primary);
}

.content {
  padding: var(--sp-8);
  display: flex;
  flex-direction: column;
  gap: var(--sp-8);
  max-width: 1080px;
}

/* === HERO INPUT === */
.hero-input {
  padding: var(--sp-6);
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-lg);
}

.hero-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--ink-tertiary);
  margin-bottom: var(--sp-3);
}

.hero-field {
  display: flex;
  gap: var(--sp-3);
}

.hero-text {
  flex: 1;
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-sm);
  color: var(--ink-primary);
  padding: var(--sp-3) var(--sp-4);
  font-size: 15px;
  font-family: inherit;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.hero-text:hover { border-color: var(--control-border-hover); }
.hero-text:focus { outline: none; border-color: var(--control-border-focus); box-shadow: 0 0 0 3px var(--brand-muted); }
.hero-text::placeholder { color: var(--ink-muted); }

.btn-hero {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-3) var(--sp-5);
  background: var(--brand);
  color: var(--surface-0);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  white-space: nowrap;
  transition: transform var(--duration-fast) var(--ease-out), opacity var(--duration-fast) var(--ease-out);
}
.btn-hero:hover:not(:disabled) { opacity: 0.9; }
.btn-hero:active:not(:disabled) { transform: scale(0.97); }
.btn-hero:disabled { opacity: 0.5; cursor: not-allowed; }

/* === SETTINGS GRID === */
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-8);
}

@media (max-width: 860px) {
  .settings-grid { grid-template-columns: 1fr; }
}

.settings-col {
  display: flex;
  flex-direction: column;
  gap: var(--sp-6);
}

/* === SECTIONS === */
.section {
  padding: var(--sp-5);
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--ink-tertiary);
  margin-bottom: var(--sp-4);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* === FIELDS === */
.field {
  margin-bottom: var(--sp-4);
}

.field:last-child { margin-bottom: 0; }

.field-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--ink-secondary);
  margin-bottom: var(--sp-1);
}

.field-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-4);
  margin-bottom: var(--sp-4);
}

.field-group.triple { grid-template-columns: 1fr 1fr 1fr; }

.field-group .field { margin-bottom: 0; }

/* === CONTROLS === */
.control {
  width: 100%;
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-xs);
  color: var(--ink-primary);
  padding: var(--sp-2) var(--sp-3);
  font-size: 13px;
  font-family: inherit;
  transition: border-color var(--duration-fast) var(--ease-out);
}

.control:hover { border-color: var(--control-border-hover); }
.control:focus { outline: none; border-color: var(--control-border-focus); box-shadow: 0 0 0 2px var(--brand-muted); }

select.control { cursor: pointer; }

.textarea { resize: vertical; line-height: 1.5; }

/* Range */
.range-field {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.range {
  flex: 1;
  accent-color: var(--brand);
  cursor: pointer;
  height: 4px;
}

.range-badge {
  font-size: 12px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--brand);
  min-width: 36px;
  text-align: right;
}

/* Color */
.color-field {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
}

.color-swatch {
  width: 28px;
  height: 28px;
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-xs);
  background: none;
  cursor: pointer;
  padding: 0;
}

.color-hex {
  font-size: 12px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  color: var(--ink-tertiary);
}

/* Ratio picker (signature element) */
.ratio-picker {
  display: flex;
  gap: var(--sp-2);
}

.ratio-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--sp-1);
  padding: var(--sp-3) var(--sp-2);
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-xs);
  color: var(--ink-tertiary);
  font-size: 11px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: border-color var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}

.ratio-btn:hover { border-color: var(--control-border-hover); color: var(--ink-secondary); }
.ratio-btn.active { border-color: var(--brand); color: var(--brand); background: var(--brand-subtle); }

.ratio-icon {
  display: block;
  border: 1.5px solid currentColor;
  border-radius: 2px;
}

.ratio-icon.portrait { width: 14px; height: 22px; }
.ratio-icon.landscape { width: 22px; height: 14px; }

/* Toggle */
.toggle-wrap {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.toggle-input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-track {
  width: 32px;
  height: 18px;
  background: var(--ink-muted);
  border-radius: 9px;
  position: relative;
  transition: background var(--duration-fast) var(--ease-out);
}

.toggle-input:checked + .toggle-track {
  background: var(--brand);
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: var(--ink-primary);
  border-radius: 50%;
  transition: transform var(--duration-fast) var(--ease-out);
}

.toggle-input:checked + .toggle-track .toggle-thumb {
  transform: translateX(14px);
}

/* === GENERATE BUTTON === */
.btn-generate {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: var(--sp-4) var(--sp-6);
  background: var(--brand);
  color: var(--surface-0);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  letter-spacing: -0.01em;
  transition: transform var(--duration-fast) var(--ease-out), opacity var(--duration-fast) var(--ease-out);
}

.btn-generate:hover:not(:disabled) { opacity: 0.92; }
.btn-generate:active:not(:disabled) { transform: scale(0.97); }
.btn-generate:disabled { opacity: 0.4; cursor: not-allowed; }

/* Spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* === TASK MONITOR === */
.task-monitor {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
  padding: var(--sp-5);
}

.task-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sp-3);
}

.task-info {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.task-badge {
  display: inline-block;
  padding: 2px var(--sp-2);
  border-radius: var(--radius-xs);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-processing { background: var(--brand-muted); color: var(--brand); }
.badge-success { background: var(--success-muted); color: var(--success); }
.badge-danger { background: var(--danger-muted); color: var(--danger); }

.task-id {
  font-size: 12px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  color: var(--ink-muted);
}

.task-pct {
  font-size: 20px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}

.progress-track {
  width: 100%;
  height: 3px;
  background: var(--edge);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--sp-3);
}

.progress-bar {
  height: 100%;
  background: var(--brand);
  border-radius: 2px;
  transition: width 0.5s var(--ease-out);
}

.terminal {
  max-height: 180px;
  overflow-y: auto;
  background: var(--surface-0);
  border: 1px solid var(--edge);
  border-radius: var(--radius-xs);
  padding: var(--sp-3);
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 11px;
  line-height: 1.6;
  color: var(--ink-tertiary);
}

.terminal pre { white-space: pre-wrap; word-break: break-all; }

.results {
  margin-top: var(--sp-4);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--sp-4);
}

.result-video {
  width: 100%;
  border-radius: var(--radius-sm);
  background: var(--surface-0);
}

/* === EMPTY STATE === */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--sp-12) var(--sp-6);
  background: var(--surface-1);
  border: 1px dashed var(--edge-strong);
  border-radius: var(--radius-lg);
  max-width: 600px;
  margin: var(--sp-8) auto;
  gap: var(--sp-4);
}

.empty-icon {
  color: var(--brand);
  opacity: 0.8;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: var(--sp-2);
}

.empty-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink-primary);
}

.empty-desc {
  font-size: 13px;
  color: var(--ink-secondary);
  max-width: 320px;
  line-height: 1.6;
}

/* === LOADING STATE === */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--sp-3);
  padding: var(--sp-12) 0;
}

.loading-text {
  font-size: 13px;
  color: var(--ink-secondary);
}

/* === TASKS GRID & CARD === */
.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--sp-6);
}

.task-card {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
  padding: var(--sp-5);
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
  transition: border-color var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out);
}

.task-card:hover {
  border-color: var(--edge-strong);
  transform: translateY(-2px);
}

.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-card-info {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
}

.task-card-id {
  font-size: 11px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  color: var(--ink-muted);
}

.task-card-actions {
  display: flex;
  gap: var(--sp-1);
}

.btn-icon {
  background: none;
  border: none;
  color: var(--ink-secondary);
  padding: var(--sp-1.5);
  border-radius: var(--radius-xs);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}

.btn-icon:hover {
  background: var(--surface-2);
  color: var(--ink-primary);
}

.btn-icon.delete:hover {
  background: var(--danger-muted);
  color: var(--danger);
}

.task-card-body {
  flex: 1;
}

.task-card-subject {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-card-script-preview {
  font-size: 12px;
  color: var(--ink-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.task-card-no-subject {
  font-size: 12px;
  color: var(--ink-muted);
  font-style: italic;
}

.task-card-progress-section {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.task-card-pct-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--ink-secondary);
}

.task-card-pct {
  font-weight: 600;
  color: var(--brand);
}

.task-card-video {
  margin-top: var(--sp-2);
}

/* === MODAL === */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--sp-6);
}

.modal-content {
  background: var(--surface-1);
  border: 1px solid var(--edge-strong);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 640px;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.modal-header {
  padding: var(--sp-4) var(--sp-5);
  border-bottom: 1px solid var(--edge);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--ink-primary);
}

.modal-close {
  background: none;
  border: none;
  color: var(--ink-secondary);
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  padding: var(--sp-1);
}

.modal-close:hover {
  color: var(--ink-primary);
}

.modal-body {
  padding: var(--sp-5);
  overflow-y: auto;
  flex: 1;
}

/* === SETTINGS VIEW === */
.settings-container {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: var(--sp-8);
  align-items: start;
}

@media (max-width: 768px) {
  .settings-container { grid-template-columns: 1fr; }
}

.settings-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--sp-2);
}

.settings-nav-btn {
  text-align: left;
  padding: var(--sp-3) var(--sp-4);
  background: none;
  border: none;
  color: var(--ink-secondary);
  font-size: 13px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out), color var(--duration-fast) var(--ease-out);
}

.settings-nav-btn:hover {
  background: var(--surface-2);
  color: var(--ink-primary);
}

.settings-nav-btn.active {
  background: var(--brand-muted);
  color: var(--brand);
  font-weight: 600;
}

.settings-content {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-lg);
  padding: var(--sp-6);
  display: flex;
  flex-direction: column;
  gap: var(--sp-6);
}

.settings-section-panel {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
}

.settings-panel-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink-primary);
  margin-bottom: var(--sp-1);
}

.settings-panel-desc {
  font-size: 12px;
  color: var(--ink-tertiary);
  margin-bottom: var(--sp-3);
}

.provider-fields {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
  border-left: 2px solid var(--brand-muted);
  padding-left: var(--sp-4);
  margin-top: var(--sp-2);
}

.sub-section {
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
  padding: var(--sp-4);
  display: flex;
  flex-direction: column;
  gap: var(--sp-3);
  background: var(--control-bg);
}

.sub-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-secondary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sub-section-fields {
  display: flex;
  flex-direction: column;
  gap: var(--sp-4);
  margin-top: var(--sp-2);
}

.checkbox-wrap {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: 13px;
  color: var(--ink-secondary);
  cursor: pointer;
  user-select: none;
}

.checkbox-wrap input[type="checkbox"] {
  accent-color: var(--brand);
  cursor: pointer;
}

.divider {
  height: 1px;
  background: var(--edge);
  margin: var(--sp-2) 0;
}

.settings-actions {
  display: flex;
  align-items: center;
  gap: var(--sp-4);
  margin-top: var(--sp-4);
  border-top: 1px solid var(--edge);
  padding-top: var(--sp-6);
}

.settings-actions .btn-generate {
  width: auto;
  min-width: 140px;
}

.save-success-msg {
  font-size: 13px;
  color: var(--success);
  font-weight: 500;
}

.control.input {
  width: 100%;
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-xs);
  color: var(--ink-primary);
  padding: var(--sp-2) var(--sp-3);
  font-size: 13px;
  font-family: inherit;
  transition: border-color var(--duration-fast) var(--ease-out);
}
.control.input:hover { border-color: var(--control-border-hover); }
.control.input:focus { outline: none; border-color: var(--control-border-focus); box-shadow: 0 0 0 2px var(--brand-muted); }

/* === FILE UPLOADER === */
.file-uploader {
  position: relative;
  border: 1px dashed var(--control-border);
  background: var(--control-bg);
  border-radius: var(--radius-xs);
  padding: var(--sp-3) var(--sp-4);
  text-align: center;
  cursor: pointer;
  transition: border-color var(--duration-fast) var(--ease-out), background-color var(--duration-fast) var(--ease-out);
}

.file-uploader:hover {
  border-color: var(--brand);
  background: var(--brand-subtle);
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-uploader-content {
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 13px;
  color: var(--ink-secondary);
  pointer-events: none;
}

.file-uploader-placeholder {
  color: var(--ink-tertiary);
}

.file-uploaded-name {
  display: inline-flex;
  align-items: center;
  gap: var(--sp-2);
  color: var(--brand);
  font-weight: 500;
  pointer-events: auto;
}

.btn-remove-file {
  background: none;
  border: none;
  color: var(--ink-tertiary);
  font-size: 16px;
  cursor: pointer;
  padding: 0 var(--sp-1);
}

.btn-remove-file:hover {
  color: var(--danger);
}

.btn-preview-voice {
  background: var(--control-bg);
  border: 1px solid var(--control-border);
  border-radius: var(--radius-xs);
  color: var(--ink-secondary);
  padding: 0 var(--sp-3);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--sp-1);
  transition: border-color var(--duration-fast) var(--ease-out), background-color var(--duration-fast) var(--ease-out);
}
.btn-preview-voice:hover:not(:disabled) {
  border-color: var(--control-border-hover);
  color: var(--ink-primary);
  background: var(--surface-2);
}
.btn-preview-voice:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* === YOUTUBE DASHBOARD STYLES === */
.youtube-dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--sp-6);
}

.channel-card {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-lg);
  padding: var(--sp-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--sp-4);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.channel-profile {
  display: flex;
  align-items: center;
  gap: var(--sp-4);
}

.channel-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid var(--brand);
  background: var(--surface-3);
  object-fit: cover;
}

.channel-avatar-placeholder {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid var(--brand);
  background: var(--surface-3);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  font-weight: bold;
  color: var(--brand);
}

.channel-meta {
  display: flex;
  flex-direction: column;
}

.channel-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--ink-primary);
  line-height: 1.2;
}

.channel-handle {
  font-size: 13px;
  color: var(--ink-secondary);
}

.channel-stats-row {
  display: flex;
  gap: var(--sp-6);
}

.channel-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 800;
  color: var(--brand);
  line-height: 1;
}

.stat-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-tertiary);
  margin-top: var(--sp-1);
}

.youtube-subtabs {
  display: flex;
  border-bottom: 1px solid var(--edge);
  gap: var(--sp-4);
}

.subtab-btn {
  background: none;
  border: none;
  padding: var(--sp-3) var(--sp-1);
  color: var(--ink-secondary);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  transition: color var(--duration-fast) var(--ease-out);
}

.subtab-btn:hover {
  color: var(--ink-primary);
}

.subtab-btn.active {
  color: var(--brand);
}

.subtab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--brand);
  border-radius: 1px;
}

.subtab-content {
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.youtube-videos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--sp-4);
}

.yt-video-card {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: transform var(--duration-normal) var(--ease-out), border-color var(--duration-normal) var(--ease-out), box-shadow var(--duration-normal) var(--ease-out);
}

.yt-video-card:hover {
  transform: translateY(-2px);
  border-color: var(--edge-strong);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.yt-thumb-wrap {
  position: relative;
  aspect-ratio: 16/9;
  background: var(--surface-3);
  overflow: hidden;
}

.yt-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--duration-normal) var(--ease-out);
}

.yt-video-card:hover .yt-thumb {
  transform: scale(1.03);
}

.yt-play-btn {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.9);
  background: rgba(232, 178, 80, 0.9);
  color: #0c0d11;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--duration-fast) var(--ease-out), transform var(--duration-fast) var(--ease-out);
}

.yt-play-btn svg {
  margin-left: 2px;
}

.yt-thumb-wrap:hover .yt-play-btn {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.yt-play-btn:hover {
  background: var(--brand-hover);
  transform: translate(-50%, -50%) scale(1.05) !important;
}

.yt-card-body {
  padding: var(--sp-4);
}

.yt-video-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  height: 40px;
  line-height: 1.4;
  margin-bottom: var(--sp-1);
}

.yt-video-title-large {
  font-size: 18px;
  font-weight: 700;
  color: var(--ink-primary);
  margin-bottom: var(--sp-2);
  line-height: 1.3;
}

.yt-video-channel {
  font-size: 12px;
  color: var(--brand);
  font-weight: 500;
  margin-bottom: var(--sp-1);
}

.yt-video-date {
  font-size: 11px;
  color: var(--ink-tertiary);
  margin-bottom: var(--sp-3);
}

.yt-video-stats {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--edge);
  padding-top: var(--sp-3);
}

.yt-stat {
  display: flex;
  align-items: center;
  gap: var(--sp-1);
  color: var(--ink-secondary);
  font-size: 12px;
}

.yt-stat svg {
  color: var(--ink-tertiary);
}

.trends-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--sp-4);
}

.search-bar-wrap {
  margin-bottom: var(--sp-6);
  max-width: 680px;
}

.search-error-box {
  background: var(--danger-muted);
  border: 1px solid var(--danger);
  color: var(--ink-primary);
  border-radius: var(--radius-md);
  padding: var(--sp-3) var(--sp-4);
  font-size: 13px;
  margin-bottom: var(--sp-6);
  animation: fadeIn 0.2s ease-out;
}

.searched-video-result {
  max-width: 800px;
  margin: 0 auto;
}

.yt-video-card.detail-view {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 0;
}

@media (max-width: 768px) {
  .yt-video-card.detail-view {
    grid-template-columns: 1fr;
  }
}

.yt-video-card.detail-view .yt-thumb-wrap {
  aspect-ratio: 16/9;
  height: 100%;
}

.yt-play-btn.large {
  width: 64px;
  height: 64px;
  opacity: 0.85;
}

.yt-play-btn.large svg {
  margin-left: 4px;
  width: 28px;
  height: 28px;
}

.large-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--sp-3);
  margin: var(--sp-4) 0;
  border: none;
  padding: 0;
}

.yt-stat-large {
  background: var(--surface-2);
  border: 1px solid var(--edge);
  border-radius: var(--radius-sm);
  padding: var(--sp-3);
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.yt-stat-large .stat-icon {
  font-size: 24px;
}

.yt-stat-large .stat-text {
  display: flex;
  flex-direction: column;
}

.yt-stat-large .stat-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink-primary);
  line-height: 1.2;
}

.yt-stat-large .stat-name {
  font-size: 11px;
  color: var(--ink-tertiary);
  text-transform: uppercase;
}

.yt-video-desc-box {
  background: var(--surface-2);
  border: 1px solid var(--edge);
  border-radius: var(--radius-sm);
  padding: var(--sp-3);
  margin-top: var(--sp-4);
}

.yt-video-desc-box .desc-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--brand);
  margin-bottom: var(--sp-2);
}

.yt-video-desc-box .desc-text {
  font-size: 12px;
  color: var(--ink-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 160px;
  overflow-y: auto;
  font-family: inherit;
}

.yt-status-badge {
  position: absolute;
  top: var(--sp-2);
  right: var(--sp-2);
  padding: 2px var(--sp-2);
  border-radius: var(--radius-xs);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  z-index: 10;
  backdrop-filter: blur(4px);
}

.yt-status-badge.public {
  background: rgba(62, 201, 122, 0.85); /* success */
  color: #edeef0;
}

.yt-status-badge.private {
  background: rgba(232, 84, 84, 0.85); /* danger */
  color: #edeef0;
}

.yt-status-badge.unlisted {
  background: rgba(232, 168, 64, 0.85); /* warning */
  color: #edeef0;
}

.yt-status-badge.scheduled {
  background: rgba(232, 178, 80, 0.85); /* brand */
  color: #0c0d11;
}

.analytics-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--sp-4);
  margin-bottom: var(--sp-6);
}

@media (max-width: 1024px) {
  .analytics-section {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
  padding: var(--sp-4);
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sp-4);
}

.chart-title {
  font-size: var(--sp-4);
  font-weight: 700;
  color: var(--ink-primary);
}

.metric-selector {
  display: flex;
  background: var(--surface-2);
  border: 1px solid var(--edge);
  border-radius: var(--radius-sm);
  padding: 2px;
  gap: 2px;
}

.metric-btn {
  border: none;
  background: transparent;
  color: var(--ink-secondary);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  padding: var(--sp-1) var(--sp-3);
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.metric-btn:hover {
  color: var(--ink-primary);
}

.metric-btn.active {
  background: var(--brand);
  color: #0c0d11;
}

.svg-chart-container {
  position: relative;
  width: 100%;
  height: 220px;
}

.trend-svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.chart-node {
  cursor: pointer;
  transition: r var(--duration-fast) var(--ease-out), fill var(--duration-fast) var(--ease-out);
}

.chart-node:hover {
  r: 8px;
}

.chart-tooltip-display {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  background: var(--surface-2);
  border: 1px solid var(--edge);
  border-radius: var(--radius-sm);
  padding: var(--sp-3);
  margin-top: var(--sp-4);
  animation: fadeIn 0.2s ease-out;
}

.tooltip-thumb {
  width: 64px;
  aspect-ratio: 16/9;
  object-fit: cover;
  border-radius: var(--radius-xs);
  flex-shrink: 0;
}

.tooltip-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex-grow: 1;
}

.tooltip-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.tooltip-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--ink-tertiary);
}

.tooltip-value {
  color: var(--brand);
}

.chart-tooltip-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 56px;
  font-size: 12px;
  color: var(--ink-tertiary);
  border: 1px dashed var(--edge);
  border-radius: var(--radius-sm);
  margin-top: var(--sp-4);
}

.insights-card {
  background: var(--surface-1);
  border: 1px solid var(--edge);
  border-radius: var(--radius-md);
  padding: var(--sp-4);
  display: flex;
  flex-direction: column;
}

.insights-title {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-tertiary);
  margin-bottom: var(--sp-4);
}

.insights-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--sp-3);
  margin-bottom: var(--sp-4);
}

.insight-metric {
  background: var(--surface-2);
  border: 1px solid var(--edge);
  border-radius: var(--radius-sm);
  padding: var(--sp-3);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.insight-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--ink-tertiary);
  letter-spacing: 0.02em;
}

.insight-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--ink-primary);
  margin-top: 2px;
}

.insight-sub {
  font-size: 11px;
  color: var(--brand);
  margin-top: 2px;
}

.explanation-box {
  background: rgba(232, 178, 80, 0.06);
  border: 1px solid rgba(232, 178, 80, 0.2);
  border-radius: var(--radius-sm);
  padding: var(--sp-3);
  display: flex;
  gap: var(--sp-2.5);
  flex-grow: 1;
}

.explanation-icon {
  font-size: var(--sp-5);
  line-height: 1;
}

.explanation-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.explanation-header {
  font-size: 12px;
  font-weight: 700;
  color: var(--brand);
  margin-bottom: 2px;
}

.explanation-desc {
  font-size: 11px;
  color: var(--ink-secondary);
  line-height: 1.4;
}
</style>
