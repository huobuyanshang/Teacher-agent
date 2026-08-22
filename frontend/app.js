const { createApp } = Vue;

createApp({
  data() {
    return {
      topic: "",
      apiKey: localStorage.getItem("agent_lecturer_api_key") || "",
      model: localStorage.getItem("agent_lecturer_model") || "deepseek-chat",
      loading: false,
      loadingCourses: false,
      error: "",
      health: { mode: "no-key", has_api_key: false },
      courses: [],
      previewUrl: "",
      currentTitle: "",
      showSettings: false,
    };
  },
  async mounted() {
    await this.refreshHealth();
    await this.loadCourses();
    this.$nextTick(this.syncHistoryHeight);
    window.addEventListener("resize", this.syncHistoryHeight);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.syncHistoryHeight);
  },
  watch: {
    showSettings() {
      this.$nextTick(this.syncHistoryHeight);
    },
    loading() {
      this.$nextTick(this.syncHistoryHeight);
    },
    error() {
      this.$nextTick(this.syncHistoryHeight);
    },
  },
  computed: {
    displayMode() {
      return this.apiKey.trim() ? "deepseek" : this.health.mode;
    },
    modeText() {
      if (this.apiKey.trim()) {
        return "已填 API Key";
      }
      return this.health.mode === "deepseek" ? "已连接 DeepSeek" : "未配置 API Key";
    },
  },
  methods: {
    async refreshHealth() {
      try {
        const response = await fetch("/api/health");
        this.health = await response.json();
      } catch {
        this.health = { mode: "no-key", has_api_key: false };
      }
    },
    async loadCourses() {
      this.loadingCourses = true;
      try {
        const response = await fetch("/api/courses");
        const data = await response.json();
        this.courses = data.courses || [];
      } catch {
        this.courses = [];
      } finally {
        this.loadingCourses = false;
        this.$nextTick(this.syncHistoryHeight);
      }
    },
    async generate() {
      const topic = this.topic.trim();
      if (!topic) {
        this.error = "请先填写学习主题";
        return;
      }
      this.error = "";
      this.loading = true;
      try {
        const response = await fetch("/api/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            topic,
            api_key: this.apiKey || null,
            model: this.model || null,
          }),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || "生成失败，请稍后重试");
        }
        await this.loadCourses();
        this.openCourse({ title: data.title, file_url: data.file_url });
      } catch (err) {
        this.error = err.message || "生成失败";
      } finally {
        this.loading = false;
      }
    },
    openCourse(course) {
      this.previewUrl = course.file_url;
      this.currentTitle = course.title;
    },
    closePreview() {
      this.previewUrl = "";
      this.currentTitle = "";
    },
    saveSettings() {
      localStorage.setItem("agent_lecturer_api_key", this.apiKey.trim());
      localStorage.setItem("agent_lecturer_model", this.model.trim());
      this.showSettings = false;
      this.refreshHealth();
    },
    syncHistoryHeight() {
      const composer = this.$refs.composerPanel;
      const history = this.$refs.historyPanel;
      if (!composer || !history) {
        return;
      }
      history.style.height = `${composer.getBoundingClientRect().height}px`;
    },
  },
}).mount("#app");
