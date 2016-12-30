'use strict';

(function ($) {
  'use strict';

  var SignUp = {
    Constants: {
      FORM_WIZARD_NEXT_SELECTOR: '.btn-next',
      FORM_WIZARD_PREVIOUS_SELECTOR: '.btn-previous'
    },
    CssClasses: {
      FORM_GROUP: 'form-group',
      FORM_CONTROL: 'form-control',
      FORM_WIZARD: 'form-wizard',
      FORM_WIZARD_TAB: 'steps'
    },
    init: function init() {
      this.$form = $('.' + this.CssClasses.FORM_WIZARD);
      this.$passwordToggler = $('[name="password_toggler"]');
      this.$passwordWrapper = this.$passwordToggler.closest('.' + this.CssClasses.FORM_GROUP);
      this.$passwordInput = this.$passwordWrapper.find('.' + this.CssClasses.FORM_CONTROL);

      this.createFormWizard().bindEvents();
    },
    bindEvents: function bindEvents() {
      this.$passwordToggler.on('change.e.app', this.handlePasswordToggle.bind(this));
    },
    handlePasswordToggle: function handlePasswordToggle(evt) {
      if (this.$passwordToggler.is(':checked')) {
        this.$passwordInput.attr('type', 'text').attr('autocapitalize', 'off').attr('autocomplete', 'off').attr('autocorrect', 'off').attr('spellcheck', 'false');
      } else {
        this.$passwordInput.attr('type', 'password');
      }

      this.$passwordInput.focus();
    },
    createFormWizard: function createFormWizard() {
      var options = this.getFormWizardOptions();
      options.onNext = this.formWizardNextHandler.bind(this);
      options.onTabClick = this.formWizardTabClickHandler.bind(this);

      this.$form.bootstrapWizard(options);

      return this;
    },
    formWizardNextHandler: function formWizardNextHandler(tab, navigation, index) {
      return this.$form.valid();
    },
    formWizardTabClickHandler: function formWizardTabClickHandler(tab, navigation, index) {
      return true; // return this.$form.valid(); (production mode)
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
    },
    getFormWizardOptions: function getFormWizardOptions() {
      return this.getCreateOptions('form_wizard', function (options, prop, key, val) {
        key = prop === 'CssClasses' ? key + 'Class' : key;
        return options[key] = val;
      });
    }
  };

  SignUp.init();
})(jQuery);
