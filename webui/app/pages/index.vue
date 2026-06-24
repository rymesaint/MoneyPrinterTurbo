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
          {{ activeTab === 'create' ? tr('Create Video') : activeTab === 'tasks' ? tr('Tasks') : tr('Settings') }}
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
                </select>
              </div>
              <div class="field" v-if="form.tts_server !== 'no-voice'">
                <label class="field-label">{{ tr('Voice') }}</label>
                <select v-model="form.voice_name" class="control select">
                  <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.name }}</option>
                </select>
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
          <div v-if="activeTask.state === 2 && activeTask.videos" class="results">
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
              <div class="task-card-progress-section" v-if="t.state === 1">
                <div class="task-card-pct-row">
                  <span>{{ tr('Progress') }}</span>
                  <span class="task-card-pct">{{ t.progress ?? 0 }}%</span>
                </div>
                <div class="progress-track">
                  <div class="progress-bar" :style="{ width: (t.progress ?? 0) + '%' }"></div>
                </div>
              </div>

              <!-- Results video preview if completed -->
              <div v-if="t.state === 2 && t.videos && t.videos.length" class="task-card-video">
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
              <p class="settings-panel-desc">{{ tr('API keys used to download video clips from Pexels, Pixabay, and Coverr.') }}</p>
              
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
const activeTab = ref<'create' | 'tasks' | 'settings'>('create')

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
  if (activeTask.value.state === 2) return 'badge-success'
  if (activeTask.value.state === 3) return 'badge-danger'
  return 'badge-processing'
})

const taskStatusLabel = computed(() => {
  if (!activeTask.value) return ''
  if (activeTask.value.state === 2) return tr('Complete')
  if (activeTask.value.state === 3) return tr('Failed')
  return tr('Processing')
})

const taskPctColor = computed(() => {
  if (!activeTask.value) return 'var(--ink-tertiary)'
  if (activeTask.value.state === 2) return 'var(--success)'
  if (activeTask.value.state === 3) return 'var(--danger)'
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
        if (res.data.state === 2 || res.data.state === 3) { isGenerating.value = false; return }
      }
    } catch { /* ignore */ }
  }
}

async function streamLog(taskId: string) {
  for await (const chunk of api.streamTaskLog(taskId)) {
    taskLog.value += chunk
    if (activeTask.value?.state === 2 || activeTask.value?.state === 3) return
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
  if (state === 2) return 'badge-success'
  if (state === 3) return 'badge-danger'
  return 'badge-processing'
}

function getTaskStatusLabel(state: number) {
  if (state === 2) return tr('Complete')
  if (state === 3) return tr('Failed')
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
      if (currentTask && (currentTask.state === 2 || currentTask.state === 3)) {
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
</style>
