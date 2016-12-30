'use strict';

(function ($) {
  "use strict";

  var Compose = {
    Constants: {
      TOOLTIP_CONTAINER: 'body',
      TOOLTIP_PLACEMENT: 'bottom',
      TOOLTIP_TRIGGER: 'hover',
      WYSIWYG_SELECTION_COLOR: 'darkgrey'
    },
    CssClasses: {
      COMPOSE_EDITOR: 'compose-editor',
      COMPOSE_TOOLBAR: 'compose-toolbar',
      WYSIWYG_ACTIVE_TOOLBAR: 'btn-default',
      BUTTON: 'btn'
    },
    init: function init() {
      this.$editor = $('.' + this.CssClasses.COMPOSE_EDITOR);
      this.$toolbar = $('.' + this.CssClasses.COMPOSE_TOOLBAR);
      this.$btns = this.$toolbar.find('.' + this.CssClasses.BUTTON);

      this.addEditorTo(this.$editor);
      this.addTooltipTo(this.$btns);

      this.bindEvents();
    },
    bindEvents: function bindEvents() {
      // None for now.
    },
    addEditorTo: function addEditorTo($el) {
      var options = this.getWysiwygOptions();
      $el.wysiwyg(options);
    },
    addTooltipTo: function addTooltipTo($el) {
      var options = this.getTooltipOptions();
      $el.tooltip(options);
    },
    getWysiwygOptions: function getWysiwygOptions() {
      return this.getCreateOptions('sticky', function (options, prop, key, val) {
        key = prop === 'CssClasses' ? key + 'Class' : key;
        return options[key] = val;
      });
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

  Compose.init();
})(jQuery);
