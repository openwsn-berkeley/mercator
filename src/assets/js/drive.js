'use strict';

(function ($) {
  "use strict";

  var util = {
    pluralize: function pluralize(word, count) {
      return count === 1 ? word : word + 's';
    },
    format: function format() {
      var str = arguments[0];
      for (var i = 1; i < arguments.length; i++) {
        var regEx = new RegExp('\\{' + (i - 1) + '\\}', 'gm');
        str = str.replace(regEx, arguments[i]);
      }
      return str;
    }
  };

  var Drive = {
    Constants: {
      TOOLTIP_CONTAINER: 'body',
      TOOLTIP_PLACEMENT: 'left',
      TOOLTIP_TRIGGER: 'hover',
      UPLOADER_AUTO_UPLOAD: true,
      UPLOADER_SEQUENTIAL_UPLOADS: true
    },
    CssClasses: {
      DRIVE: 'drive',
      DRIVE_TOOLBAR: 'drive-toolbar',
      DRIVE_UPLOADER: 'drive-uploader',
      DRIVE_UPLOADER_BTN: 'drive-uploader-btn',
      DRIVE_DRAGOVER: 'drive-dragover',
      UPLOADER_FILES_CONTAINER: 'file-list',
      HAS_FILES: 'has-files',
      HOVER: 'hover',
      SELECTED: 'selected'
    },
    init: function init() {
      this.$body = $(document.body);
      this.$drive = $('.' + this.CssClasses.DRIVE);
      this.$toolbar = $('.' + this.CssClasses.DRIVE_TOOLBAR);
      this.$uploader = $('.' + this.CssClasses.DRIVE_UPLOADER);
      this.$uploaderBtn = $('.' + this.CssClasses.DRIVE_UPLOADER_BTN);
      this.$list = $('.' + this.CssClasses.UPLOADER_FILES_CONTAINER);
      this.$tooltipBtns = $('button[data-toggle]');
      this.currentFiles = [];

      this.uploader().bindEvents();
      this.tooltips();
    },
    uploader: function uploader() {
      var options = this.getUploaderOptions();

      options.dropZone = this.$drive;
      options.filesContainer = this.$list;

      this.$uploader.fileupload(options);
      return this;
    },
    tooltips: function tooltips() {
      var options = this.getTooltipOptions();
      this.$tooltipBtns.tooltip(options);
    },
    bindEvents: function bindEvents() {
      $(document).on('mouseenter.e.drive', '.file', this.handleFileMouseEnter.bind(this)).on('mouseleave.e.drive', '.file', this.handleFileMouseLeave.bind(this)).on('change.e.drive', '.file-select-input', this.handleFileSelectInputChange.bind(this)).on('dragover.e.drive', this.handleFileUploadDragover.bind(this)).on('drop.e.drive', this.handleFileUploadDrop.bind(this)).on('fileuploadstart.e.drive', this.handleFileUploadStart.bind(this)).on('fileuploaddone.e.drive', this.handleFileUploadDone.bind(this)).on('fileuploadfail.e.drive', this.handleFileUploadFail.bind(this)).on('fileuploadstop.e.drive', this.handleFileUploadStop.bind(this));

      $('[data-toggle="uploader"]').on('click.e.drive', this.handleUploaderBtnClick.bind(this));
    },
    handleFileMouseEnter: function handleFileMouseEnter(evt) {
      $(evt.currentTarget).addClass(this.CssClasses.HOVER);
    },
    handleFileMouseLeave: function handleFileMouseLeave(evt) {
      $(evt.currentTarget).removeClass(this.CssClasses.HOVER);
    },
    handleFileSelectInputChange: function handleFileSelectInputChange(evt) {
      var $checkbox = $(evt.currentTarget);
      this.selectItem($checkbox);

      this.toggleToolbar();
    },
    handleFileUploadDragover: function handleFileUploadDragover(evt) {
      var $dropZone = this.$drive,
          node = evt.target;

      clearTimeout(this.dropZoneTimeoutId);

      do {
        if ($(node).is($dropZone)) {
          $dropZone.addClass(this.CssClasses.DRIVE_DRAGOVER);
          break;
        }
      } while (node = node.parentNode);

      this.dropZoneTimeoutId = setTimeout(function () {
        $dropZone.removeClass(this.CssClasses.DRIVE_DRAGOVER);
      }.bind(this), 100);

      evt.preventDefault();
    },
    handleFileUploadDrop: function handleFileUploadDrop(evt) {
      evt.preventDefault();
    },
    handleFileUploadStart: function handleFileUploadStart(evt) {
      var state = this.hasItems();
      this.$body.toggleClass(this.CssClasses.HAS_FILES, state);
    },
    handleFileUploadDone: function handleFileUploadDone(evt, data) {
      var getFilesFromResponse = data.getFilesFromResponse,
          files = getFilesFromResponse(data);

      if (data.context) {
        data.context.each(function (idx) {
          var file = files[idx] || {
            error: 'Empty file upload result.'
          };

          this.registerUpload(file);
        }.bind(this));
      }
    },
    handleFileUploadFail: function handleFileUploadFail(evt, data) {
      if (data.context) {
        data.context.each(function (idx) {
          var file = data.files[index];
          file.error = file.error || data.errorThrown || data.i18n('unknownError');

          this.registerUpload(file);
        }.bind(this));
      }
    },
    handleFileUploadStop: function handleFileUploadStop(evt) {
      this.showCompletedNotification();
      this.showFailedNotification();

      this.currentFiles = [];
    },
    handleUploaderBtnClick: function handleUploaderBtnClick(evt) {
      this.$uploaderBtn.trigger('click');
    },
    registerUpload: function registerUpload(file) {
      this.currentFiles.push(file);
    },
    getCompletedUploads: function getCompletedUploads() {
      return this.currentFiles.filter(function (file) {
        return typeof file.error === 'undefined';
      });
    },
    getFailedUploads: function getFailedUploads() {
      return this.currentFiles.filter(function (file) {
        return typeof file.error === 'string';
      });
    },
    showNotification: function showNotification(data) {
      toastr[data.type](data.message, data.title);
    },
    showCompletedNotification: function showCompletedNotification() {
      var files = this.getCompletedUploads(),
          count,
          word;

      if (count = files.length) {
        word = util.pluralize('item', count);
        this.showNotification({
          message: util.format('Uploaded {0} {1}', count, word),
          type: 'success'
        });
      }
    },
    showFailedNotification: function showFailedNotification() {
      var files = this.getFailedUploads();

      files.forEach(function (file) {
        this.showNotification({
          title: file.name,
          message: file.error,
          type: 'error'
        });
      }.bind(this));
    },
    selectItem: function selectItem($checkbox) {
      var $item = $checkbox.closest('.file'),
          state = $checkbox.is(':checked');

      $item.toggleClass(this.CssClasses.SELECTED, state);
    },
    getItems: function getItems() {
      return this.$list.children();
    },
    hasItems: function hasItems() {
      return !!this.getItems().length;
    },
    getSelectedItems: function getSelectedItems() {
      var $items = this.getItems();
      return $items.filter('.' + this.CssClasses.SELECTED);
    },
    hasSelectedItems: function hasSelectedItems() {
      return !!this.getSelectedItems().length;
    },
    toggleToolbar: function toggleToolbar() {
      var state = this.hasSelectedItems();
      this.$toolbar.collapse(state ? 'show' : 'hide');
    },
    getUploaderOptions: function getUploaderOptions() {
      return this.getCreateOptions('uploader');
    },
    getTooltipOptions: function getTooltipOptions() {
      return this.getCreateOptions('tooltip');
    },
    getCreateOptions: function getCreateOptions(prefix, callback) {
      var regex = new RegExp('^' + prefix + '(_)?', 'i'),
          options = {};

      $.each(this, function (prop, obj) {
        if (!$.isPlainObject(obj)) return;

        $.each(obj, function (key, val) {
          if (regex.test(key)) {
            key = key.replace(regex, '').replace(/_/g, '-');
            key = $.camelCase(key.toLowerCase());

            callback && callback(options, prop, key, val) || (options[key] = val);
          }
        });
      });

      return options;
    }
  };

  Drive.init();
})(jQuery);
