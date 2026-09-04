/* SCORM 1.2 Lightweight API Wrapper */
var scorm = {
  api: null,
  findAPI: function(win) {
    var findAttempts = 0;
    while ((win.API == null) && (win.parent != null) && (win.parent != win)) {
      findAttempts++;
      if (findAttempts > 500) return null;
      win = win.parent;
    }
    return win.API;
  },
  init: function() {
    this.api = this.findAPI(window);
    if (!this.api && window.opener) {
      this.api = this.findAPI(window.opener);
    }
    if (this.api) {
      this.api.LMSInitialize("");
      this.api.LMSSetValue("cmi.core.lesson_status", "incomplete");
      this.api.LMSCommit("");
    }
  },
  complete: function(score) {
    if (this.api) {
      this.api.LMSSetValue("cmi.core.lesson_status", "completed");
      if (score !== undefined && score !== null) {
        this.api.LMSSetValue("cmi.core.score.raw", score.toString());
      }
      this.api.LMSCommit("");
    }
  },
  finish: function() {
    if (this.api) {
      this.api.LMSFinish("");
    }
  }
};

window.addEventListener("load", function() {
  scorm.init();
});

window.addEventListener("beforeunload", function() {
  scorm.finish();
});
