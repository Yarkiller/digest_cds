(function () {
  "use strict";

  function showToast(message) {
    var existing = document.querySelector(".toast");
    if (existing) existing.remove();
    var el = document.createElement("div");
    el.className = "toast";
    el.setAttribute("role", "status");
    el.textContent = message;
    document.body.appendChild(el);
    requestAnimationFrame(function () {
      el.classList.add("toast--visible");
    });
    setTimeout(function () {
      el.classList.remove("toast--visible");
      setTimeout(function () {
        el.remove();
      }, 200);
    }, 2800);
  }

  function initVoting() {
    var ballot = document.querySelector("[data-voting]");
    if (!ballot) return;

    var status = document.getElementById("vote-status");
    var confirmBtn = document.getElementById("confirm-vote");
    var selectedTopic = null;

    function selectRow(row) {
      ballot.querySelectorAll(".topic-ballot__row").forEach(function (r) {
        r.classList.remove("topic-ballot__row--selected");
        r.setAttribute("aria-checked", "false");
      });
      row.classList.add("topic-ballot__row--selected");
      row.setAttribute("aria-checked", "true");
      selectedTopic = row.getAttribute("data-topic");
      if (status) {
        status.textContent = "Ваш голос: выбран «" + selectedTopic + "» (не подтверждён)";
      }
    }

    ballot.querySelectorAll(".topic-ballot__row").forEach(function (row) {
      row.addEventListener("click", function () {
        selectRow(row);
      });
      row.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          selectRow(row);
        }
      });
    });

    if (confirmBtn) {
      confirmBtn.addEventListener("click", function () {
        if (!selectedTopic) {
          showToast("Сначала выберите тему");
          return;
        }
        if (status) {
          status.textContent = "Ваш голос: " + selectedTopic;
        }
        showToast("Голос сохранён (прототип)");
      });
    }
  }

  function initKnowledge() {
    var root = document.querySelector("[data-knowledge]");
    if (!root) return;

    var search = document.getElementById("kb-search");
    var role = document.getElementById("filter-role");
    var tag = document.getElementById("filter-tag");
    var format = document.getElementById("filter-format");
    var topic = document.getElementById("filter-topic");
    var countEl = document.getElementById("kb-count");
    var emptyEl = document.getElementById("kb-empty");
    var loadMore = document.getElementById("kb-load-more");
    var skeleton = document.getElementById("kb-skeleton");
    var rows = Array.prototype.slice.call(root.querySelectorAll(".material-list-row"));
    var extrasExpanded = false;

    function tokens(str) {
      return (str || "")
        .toLowerCase()
        .split(/[\s,.#]+/)
        .filter(Boolean);
    }

    function rowMatches(row) {
      var q = tokens(search && search.value);
      var roleVal = role ? role.value : "";
      var tagVal = tag ? tag.value : "";
      var formatVal = format ? format.value : "";
      var topicVal = topic ? topic.value : "";

      var rowRole = (row.getAttribute("data-role") || "").split(/\s+/);
      var rowTags = (row.getAttribute("data-tags") || "").split(/\s+/);
      var rowFormat = row.getAttribute("data-format") || "";
      var rowTopic = row.getAttribute("data-topic") || "";
      var keywords = (row.getAttribute("data-keywords") || "") + " " + (row.getAttribute("data-tags") || "");

      if (roleVal && rowRole.indexOf(roleVal) === -1) return false;
      if (tagVal && rowTags.indexOf(tagVal) === -1) return false;
      if (formatVal && rowFormat !== formatVal) return false;
      if (topicVal && rowTopic !== topicVal) return false;

      if (q.length) {
        var hay = keywords.toLowerCase();
        var hit = q.some(function (t) {
          return hay.indexOf(t) !== -1;
        });
        if (!hit) return false;
      }
      return true;
    }

    function applyFilters() {
      var matched = [];
      rows.forEach(function (row) {
        var ok = rowMatches(row);
        var isExtra = row.classList.contains("is-extra");
        if (!ok) {
          row.hidden = true;
          return;
        }
        matched.push(row);
        if (isExtra && !extrasExpanded) {
          row.hidden = true;
        } else {
          row.hidden = false;
        }
      });

      var visible = matched.filter(function (r) {
        return !r.hidden;
      });
      var totalMatched = matched.length;

      if (emptyEl) emptyEl.hidden = totalMatched > 0;
      if (countEl) {
        countEl.textContent =
          totalMatched === 0
            ? "Найдено 0 материалов"
            : "Показано " + visible.length + " из " + totalMatched;
      }
      if (loadMore) {
        var hasHiddenExtras = matched.some(function (r) {
          return r.classList.contains("is-extra") && r.hidden;
        });
        loadMore.hidden = !hasHiddenExtras || totalMatched === 0;
        loadMore.disabled = false;
      }
    }

    function resetFilters() {
      if (search) search.value = "";
      if (role) role.value = "";
      if (tag) tag.value = "";
      if (format) format.value = "";
      if (topic) topic.value = "";
      extrasExpanded = false;
      applyFilters();
    }

    [search, role, tag, format, topic].forEach(function (el) {
      if (!el) return;
      el.addEventListener("input", applyFilters);
      el.addEventListener("change", applyFilters);
    });

    root.querySelectorAll("[data-hint]").forEach(function (chip) {
      chip.addEventListener("click", function () {
        if (search) search.value = chip.getAttribute("data-hint") || "";
        var hint = chip.getAttribute("data-hint") || "";
        if (role) {
          if (hint.indexOf("SQL") !== -1 || hint.indexOf("аналитик") !== -1) {
            role.value = "analyst";
          } else if (hint.indexOf("RAG") !== -1 || hint.indexOf("Scientist") !== -1) {
            role.value = "ds";
          }
        }
        extrasExpanded = false;
        applyFilters();
      });
    });

    var resetBtn = document.getElementById("kb-reset");
    var emptyReset = document.getElementById("kb-empty-reset");
    if (resetBtn) resetBtn.addEventListener("click", resetFilters);
    if (emptyReset) emptyReset.addEventListener("click", resetFilters);

    if (loadMore) {
      loadMore.addEventListener("click", function () {
        if (skeleton) skeleton.hidden = false;
        loadMore.disabled = true;
        setTimeout(function () {
          extrasExpanded = true;
          if (skeleton) skeleton.hidden = true;
          applyFilters();
          showToast("Загружены дополнительные материалы");
        }, 350);
      });
    }

    applyFilters();
  }

  function initAdmin() {
    var root = document.querySelector("[data-admin]");
    if (!root) return;

    var rows = Array.prototype.slice.call(root.querySelectorAll(".admin-row"));
    var sendBtn = document.getElementById("admin-send");
    var sendHint = document.getElementById("admin-send-hint");
    var emailPreviewed = false;
    var itemModal = document.getElementById("item-preview-modal");
    var emailModal = document.getElementById("email-preview-modal");

    function selectedRows() {
      return rows.filter(function (row) {
        var cb = row.querySelector('input[type="checkbox"]');
        return cb && cb.checked;
      });
    }

    function updateSendState() {
      var selected = selectedRows();
      var hasDraft = selected.some(function (row) {
        return row.getAttribute("data-status") === "draft";
      });
      var canSend = emailPreviewed && selected.length > 0 && !hasDraft;
      if (sendBtn) sendBtn.disabled = !canSend;
      if (sendHint) {
        if (!emailPreviewed) {
          sendHint.textContent = "Сначала откройте превью письма. Send недоступен, пока в selection есть draft.";
        } else if (hasDraft) {
          sendHint.textContent = "Уберите черновики из selection или дождитесь статуса ready.";
        } else if (selected.length === 0) {
          sendHint.textContent = "Выберите хотя бы один ready-материал.";
        } else {
          sendHint.textContent = "Готово к отправке (прототип).";
        }
      }
    }

    function openModal(modal) {
      if (!modal) return;
      modal.hidden = false;
      document.body.classList.add("modal-open");
    }

    function closeModal(modal) {
      if (!modal) return;
      modal.hidden = true;
      if (!document.querySelector(".modal:not([hidden])")) {
        document.body.classList.remove("modal-open");
      }
    }

    document.querySelectorAll("[data-close-modal]").forEach(function (el) {
      el.addEventListener("click", function () {
        var modal = el.closest(".modal");
        closeModal(modal);
      });
    });

    document.getElementById("admin-select-all") &&
      document.getElementById("admin-select-all").addEventListener("click", function () {
        rows.forEach(function (row) {
          var cb = row.querySelector('input[type="checkbox"]');
          if (cb) cb.checked = true;
          row.classList.remove("admin-row--excluded");
          var excl = row.querySelector(".admin-row__exclusion");
          if (excl) {
            excl.hidden = true;
            excl.textContent = "";
          }
        });
        emailPreviewed = false;
        updateSendState();
      });

    document.getElementById("admin-approve") &&
      document.getElementById("admin-approve").addEventListener("click", function () {
        selectedRows().forEach(function (row) {
          row.classList.remove("admin-row--excluded");
          var excl = row.querySelector(".admin-row__exclusion");
          if (excl) {
            excl.hidden = true;
            excl.textContent = "";
          }
        });
        showToast("Approve: материалы в selection");
        emailPreviewed = false;
        updateSendState();
      });

    document.getElementById("admin-reject") &&
      document.getElementById("admin-reject").addEventListener("click", function () {
        selectedRows().forEach(function (row) {
          var cb = row.querySelector('input[type="checkbox"]');
          if (cb) cb.checked = false;
          row.classList.add("admin-row--excluded");
          var excl = row.querySelector(".admin-row__exclusion");
          if (excl) {
            excl.hidden = false;
            excl.textContent = "исключён админом";
          }
        });
        showToast("Reject: сняты с shortlist");
        emailPreviewed = false;
        updateSendState();
      });

    rows.forEach(function (row) {
      var cb = row.querySelector('input[type="checkbox"]');
      if (cb) {
        cb.addEventListener("change", function () {
          emailPreviewed = false;
          if (cb.checked) {
            row.classList.remove("admin-row--excluded");
            var excl = row.querySelector(".admin-row__exclusion");
            if (excl && excl.textContent === "исключён админом") {
              excl.hidden = true;
              excl.textContent = "";
            }
          }
          updateSendState();
        });
      }

      var previewBtn = row.querySelector("[data-preview]");
      if (previewBtn) {
        previewBtn.addEventListener("click", function () {
          if (!itemModal) return;
          document.getElementById("item-preview-heading").textContent =
            row.getAttribute("data-title") || "";
          document.getElementById("item-preview-dek").textContent =
            row.getAttribute("data-dek") || "";
          document.getElementById("item-preview-status").textContent =
            "Статус: " + (row.getAttribute("data-status") || "—");
          openModal(itemModal);
        });
      }
    });

    document.getElementById("admin-email-preview") &&
      document.getElementById("admin-email-preview").addEventListener("click", function () {
        var list = document.getElementById("email-preview-list");
        if (list) {
          list.innerHTML = "";
          selectedRows()
            .filter(function (row) {
              return row.getAttribute("data-status") === "ready";
            })
            .forEach(function (row) {
              var li = document.createElement("li");
              li.textContent = row.getAttribute("data-title") || "";
              list.appendChild(li);
            });
          if (!list.children.length) {
            var empty = document.createElement("li");
            empty.textContent = "Нет approved ready в selection";
            list.appendChild(empty);
          }
        }
        emailPreviewed = true;
        openModal(emailModal);
        updateSendState();
      });

    if (sendBtn) {
      sendBtn.addEventListener("click", function () {
        if (sendBtn.disabled) return;
        showToast("Дайджест отправлен (прототип)");
      });
    }

    updateSendState();
  }

  initVoting();
  initKnowledge();
  initAdmin();
})();
