'use strict';

(function ($) {
  'use strict';

  var App = {
    Constants: {
      MEDIA_QUERY_BREAKPOINT: '992px',
      TRANSITION_DELAY: 400,
      TRANSITION_DURATION: 400
    },
    CssClasses: {
      LAYOUT: 'layout',
      LAYOUT_HEADER: 'layout-header',
      LAYOUT_SIDEBAR: 'layout-sidebar',
      LAYOUT_CONTENT: 'layout-content',
      LAYOUT_FOOTER: 'layout-footer',

      LAYOUT_HEADER_FIXED: 'layout-header-fixed',
      LAYOUT_SIDEBAR_FIXED: 'layout-sidebar-fixed',
      LAYOUT_FOOTER_FIXED: 'layout-footer-fixed',

      LAYOUT_SIDEBAR_COLLAPSED: 'layout-sidebar-collapsed',
      LAYOUT_SIDEBAR_STICKY: 'layout-sidebar-sticky',

      SIDENAV: 'sidenav',
      SIDENAV_BTN: 'sidenav-toggler',
      SIDENAV_COLLAPSED: 'sidenav-collapsed',

      SEARCH_FORM: 'navbar-search',
      SEARCH_FORM_BTN: 'navbar-search-toggler',
      SEARCH_FORM_COLLAPSED: 'navbar-search-collapsed',

      CUSTOM_SCROLLBAR: 'custom-scrollbar',

      CARD: 'card',
      CARD_BODY: 'card-body',
      CARD_COLLAPSED: 'card-collapsed',
      CARD_FOCUSED: 'card-focused',
      CARD_TOGGLER_BTN: 'card-toggler',
      CARD_RELOAD_BTN: 'card-reload',
      CARD_FOCUS_BTN: 'card-focus',
      CARD_REMOVE_BTN: 'card-remove',
      CARD_FOCUS_MODE: 'card-focus-mode',

      THEME_PANEL: 'theme-panel',
      THEME_PANEL_BTN: 'theme-panel-toggler',
      THEME_PANEL_COLLAPSED: 'theme-panel-collapsed',

      SPINNER: 'spinner',
      SPINNER_PRIMARY: 'spinner-primary',

      COLLAPSED: 'collapsed'
    },
    Options: {
      // Custom scrollbar options
      CUSTOM_SCROLLBAR_BAR_CLASS: 'custom-scrollbar-gripper',
      CUSTOM_SCROLLBAR_CLASS: 'custom-scrollbar',
      CUSTOM_SCROLLBAR_DISTANCE: '5px',
      CUSTOM_SCROLLBAR_HEIGHT: '100%',
      CUSTOM_SCROLLBAR_POSITION: 'right',
      CUSTOM_SCROLLBAR_RAIL_CLASS: 'custom-scrollbar-track',
      CUSTOM_SCROLLBAR_SIZE: '6px',
      CUSTOM_SCROLLBAR_TOUCH_SCROLL_STEP: 50,
      CUSTOM_SCROLLBAR_WHEEL_STEP: 10,
      CUSTOM_SCROLLBAR_WIDTH: '100%',
      CUSTOM_SCROLLBAR_WRAPPER_CLASS: 'custom-scrollable-area',

      // Side navigation options
      SIDENAV_CLASS: 'sidenav',
      SIDENAV_ACTIVE_CLASS: 'open',
      SIDENAV_COLLAPSE_CLASS: 'collapse',
      SIDENAV_COLLAPSE_IN_CLASS: 'in',
      SIDENAV_COLLAPSING_CLASS: 'collapsing',

      // Select2 options
      SELECT2_THEME: 'bootstrap',
      SELECT2_WIDTH: '100%',

      // Sticky options
      STICKY: 'sticky-scrollbar',
      STICKY_WRAPPER: 'sticky-scrollable-area',
      STICKY_OFF_RESOLUTIONS: -768,
      STICKY_TOP: 55,

      // BlockUI options
      BLOCK_UI_CSS_BACKGROUND_COLOR: 'none',
      BLOCK_UI_CSS_BORDER: 'none',
      BLOCK_UI_CSS_PADDING: 0,
      BLOCK_UI_OVERLAY_CSS_BACKGROUND_COLOR: '#fff',
      BLOCK_UI_OVERLAY_CSS_CURSOR: 'wait',
      BLOCK_UI_OVERLAY_CSS_OPACITY: 0.8
    },
    KeyCodes: {
      S: 83,
      OPEN_SQUARE_BRACKET: 219,
      CLOSE_SQUARE_BRACKET: 221
    },
    init: function init() {
      this.$document = $(document);
      this.$body = $(document.body);
      this.$layout = $('.' + this.CssClasses.LAYOUT);
      this.$header = $('.' + this.CssClasses.LAYOUT_HEADER);
      this.$sidebar = $('.' + this.CssClasses.LAYOUT_SIDEBAR);
      this.$content = $('.' + this.CssClasses.LAYOUT_CONTENT);
      this.$footer = $('.' + this.CssClasses.LAYOUT_FOOTER);
      this.$scrollableArea = $('.' + this.CssClasses.CUSTOM_SCROLLBAR);
      this.$sidenav = $('.' + this.CssClasses.SIDENAV);
      this.$sidenavBtn = $('.' + this.CssClasses.SIDENAV_BTN);
      this.$searchForm = $('.' + this.CssClasses.SEARCH_FORM);
      this.$searchFormBtn = $('.' + this.CssClasses.SEARCH_FORM_BTN);
      this.$cardTogglerBtn = $('.' + this.CssClasses.CARD_TOGGLER_BTN);
      this.$cardReloadBtn = $('.' + this.CssClasses.CARD_RELOAD_BTN);
      this.$cardFocusBtn = $('.' + this.CssClasses.CARD_FOCUS_BTN);
      this.$cardRemoveBtn = $('.' + this.CssClasses.CARD_REMOVE_BTN);
      this.$themePanel = $('.' + this.CssClasses.THEME_PANEL);
      this.$themePanelBtn = $('.' + this.CssClasses.THEME_PANEL_BTN);
      this.$themeSettings = this.$themePanel.find(':checkbox');

      var mediaQueryString = '(max-width: ' + this.Constants.MEDIA_QUERY_BREAKPOINT + ')';
      this.mediaQueryList = window.matchMedia(mediaQueryString);

      if (this.mediaQueryMatches()) {
        this.collapseSidenav();
      }

      this.addCustomScrollbarTo(this.$scrollableArea);
      this.initPlugins().bindEvents().syncThemeSettings();
    },
    bindEvents: function bindEvents() {
      this.$document.on('keydown.e.app', this.handleKeyboardEvent.bind(this));

      this.$sidenavBtn.on('click.e.app', this.handleSidenavToggle.bind(this));
      this.$sidenav.on('collapse-start.e.app', this.handleSidenavCollapseStart.bind(this)).on('expand-start.e.app', this.handleSidenavExpandStart.bind(this));

      this.$sidenav.on('collapse-end.e.app', this.handleSidebarStickyUpdate.bind(this)).on('expand-end.e.app', this.handleSidebarStickyUpdate.bind(this));

      this.$sidenav.on('shown.metisMenu.e.app', this.handleSidebarStickyUpdate.bind(this)).on('hidden.metisMenu.e.app', this.handleSidebarStickyUpdate.bind(this));

      this.$searchFormBtn.on('click.e.app', this.handleSearchFormToggle.bind(this));

      this.$cardTogglerBtn.on('click.e.app', this.handleCardToggle.bind(this));
      this.$cardReloadBtn.on('click.e.app', this.handleCardReload.bind(this));
      this.$cardFocusBtn.on('click.e.app', this.handleCardFocus.bind(this));
      this.$cardRemoveBtn.on('click.e.app', this.handleCardRemove.bind(this));

      this.$themePanelBtn.on('click.e.app', this.handleThemePanelToggle.bind(this));
      this.$themeSettings.on('change.e.app', this.handleThemeSettingsChange.bind(this));

      this.mediaQueryList.addListener(this.handleMediaQueryChange.bind(this));

      return this;
    },
    handleKeyboardEvent: function handleKeyboardEvent(evt) {
      if (/input|textarea/i.test(evt.target.tagName)) return;

      switch (evt.keyCode) {
        case this.KeyCodes.S:
          this.toggleSearchForm();
          break;
        case this.KeyCodes.OPEN_SQUARE_BRACKET:
          this.toggleSidenav();
          break;
        case this.KeyCodes.CLOSE_SQUARE_BRACKET:
          this.toggleThemePanel();
          break;
      }
    },
    handleSidenavToggle: function handleSidenavToggle(evt) {
      evt.preventDefault();
      this.toggleSidenav();
    },
    handleSidenavCollapseStart: function handleSidenavCollapseStart(evt) {
      var $input = this.getThemeSettingsBy(this.CssClasses.LAYOUT_SIDEBAR_COLLAPSED);

      $input.prop('checked', true);
    },
    handleSidenavExpandStart: function handleSidenavExpandStart(evt) {
      var $input = this.getThemeSettingsBy(this.CssClasses.LAYOUT_SIDEBAR_COLLAPSED);

      $input.prop('checked', false);
    },
    handleSidebarStickyUpdate: function handleSidebarStickyUpdate(evt) {
      if (this.isSidebarSticky()) {
        this.updateStickySidebar();
      }
    },
    handleSearchFormToggle: function handleSearchFormToggle(evt) {
      evt.preventDefault();
      this.toggleSearchForm();
    },
    handleCardToggle: function handleCardToggle(evt) {
      this.$card = $(evt.target).closest('.' + this.CssClasses.CARD);

      this.$card.toggleClass(this.CssClasses.CARD_COLLAPSED).find('.' + this.CssClasses.CARD_BODY).slideToggle();

      if (this.$card.hasClass(this.CssClasses.CARD_COLLAPSED)) {
        this.$card.attr('aria-expanded', false);
        this.$cardTogglerBtn.attr('aria-expanded', false).attr('title', 'Expand');
      } else {
        this.$card.attr('aria-expanded', true);
        this.$cardTogglerBtn.attr('aria-expanded', true).attr('title', 'Collapse');
      }

      evt.preventDefault();
    },
    handleCardReload: function handleCardReload(evt) {
      var $card = $(evt.target).closest('.' + this.CssClasses.CARD),
          options = this.getBlockUIOptions();

      $card.block(options);

      // For demo purposes
      setTimeout(function () {
        $card.unblock();
      }, 2000);
    },
    handleCardFocus: function handleCardFocus(evt) {
      this.$body.toggleClass(this.CssClasses.CARD_FOCUS_MODE);

      $(evt.target).closest('.' + this.CssClasses.CARD).toggleClass(this.CssClasses.CARD_FOCUSED);

      evt.preventDefault();
    },
    handleCardRemove: function handleCardRemove(evt) {
      this.$body.removeClass(this.CssClasses.CARD_FOCUS_MODE);

      $(evt.target).closest('.' + this.CssClasses.CARD).remove();

      evt.preventDefault();
    },
    handleThemePanelToggle: function handleThemePanelToggle(evt) {
      evt.preventDefault();
      this.toggleThemePanel();
    },
    handleThemeSettingsChange: function handleThemeSettingsChange(evt) {
      var $input = $(evt.target);

      switch ($input.attr('name')) {
        case this.CssClasses.LAYOUT_HEADER_FIXED:
          this.setHeaderFixed($input.prop('checked'));
          break;
        case this.CssClasses.LAYOUT_SIDEBAR_FIXED:
          this.setSidebarFixed($input.prop('checked'));
          break;
        case this.CssClasses.LAYOUT_SIDEBAR_STICKY:
          this.setSidebarSticky($input.prop('checked'));
          break;
        case this.CssClasses.LAYOUT_SIDEBAR_COLLAPSED:
          this.$sidenavBtn.trigger('click');
          break;
        case this.CssClasses.LAYOUT_FOOTER_FIXED:
          this.setFooterFixed($input.prop('checked'));
          break;
      }
    },
    handleMediaQueryChange: function handleMediaQueryChange(evt) {
      this[this.mediaQueryMatches() ? 'collapseSidenav' : 'expandSidenav']();
    },
    collapseSidenav: function collapseSidenav() {
      var startEvent = $.Event('collapse-start');

      this.$layout.addClass(this.CssClasses.LAYOUT_SIDEBAR_COLLAPSED);
      this.$sidenav.trigger(startEvent).css('opacity', 0);

      this.$sidenav.addClass(this.CssClasses.SIDENAV_COLLAPSED);
      this.$sidenavBtn.addClass(this.CssClasses.COLLAPSED);

      if (this.transitionTimeoutId) {
        clearTimeout(this.transitionTimeoutId);
      }

      this.transitionTimeoutId = setTimeout(function () {
        this.$sidenav.animate({ opacity: 1 }).trigger('collapse-end');
      }.bind(this), this.Constants.TRANSITION_DELAY);

      this.$sidenav.attr('aria-expanded', false);
      this.$sidenavBtn.attr('aria-expanded', false).attr('title', 'Expand sidenav ( [ )');
    },
    expandSidenav: function expandSidenav() {
      var startEvent = $.Event('expand-start');

      this.$layout.removeClass(this.CssClasses.LAYOUT_SIDEBAR_COLLAPSED);
      this.$sidenav.trigger(startEvent).css('opacity', 0);

      this.$sidenav.removeClass(this.CssClasses.SIDENAV_COLLAPSED);
      this.$sidenavBtn.removeClass(this.CssClasses.COLLAPSED);

      if (this.transitionTimeoutId) {
        clearTimeout(this.transitionTimeoutId);
      }

      this.transitionTimeoutId = setTimeout(function () {
        this.$sidenav.animate({ opacity: 1 }).trigger('expand-end');
      }.bind(this), this.Constants.TRANSITION_DELAY);

      this.$sidenav.attr('aria-expanded', true);
      this.$sidenavBtn.attr('aria-expanded', true).attr('title', 'Collapse sidenav ( [ )');
    },
    toggleSidenav: function toggleSidenav() {
      this[this.isSidenavCollapsed() ? 'expandSidenav' : 'collapseSidenav']();
    },
    isSidenavCollapsed: function isSidenavCollapsed() {
      return this.$sidenav.hasClass(this.CssClasses.SIDENAV_COLLAPSED);
    },
    toggleSearchForm: function toggleSearchForm() {
      this.$searchForm.toggleClass(this.CssClasses.SEARCH_FORM_COLLAPSED);
      this.$searchFormBtn.toggleClass(this.CssClasses.COLLAPSED);

      if (this.isSearchFormCollapsed()) {
        this.$searchForm.attr('aria-expanded', false);
        this.$searchFormBtn.attr('aria-expanded', false).attr('title', 'Expand search form ( S )');
      } else {
        this.$searchForm.attr('aria-expanded', true);
        this.$searchFormBtn.attr('aria-expanded', true).attr('title', 'Collapse search form ( S )');
      }
    },
    isSearchFormCollapsed: function isSearchFormCollapsed() {
      return this.$searchForm.hasClass(this.CssClasses.SEARCH_FORM_COLLAPSED);
    },
    toggleThemePanel: function toggleThemePanel() {
      this.$themePanel.toggleClass(this.CssClasses.THEME_PANEL_COLLAPSED);
      this.$themePanelBtn.toggleClass(this.CssClasses.COLLAPSED);

      if (this.isThemePanelCollapsed()) {
        this.$themePanel.attr('aria-expanded', false);
        this.$themePanelBtn.attr('aria-expanded', false).attr('title', 'Expand theme panel ( ] )');
      } else {
        this.$themePanel.attr('aria-expanded', true);
        this.$themePanelBtn.attr('aria-expanded', true).attr('title', 'Collapse theme panel ( ] )');
      }
    },
    isThemePanelCollapsed: function isThemePanelCollapsed() {
      return this.$themePanel.hasClass(this.CssClasses.THEME_PANEL_COLLAPSED);
    },
    syncThemeSettings: function syncThemeSettings() {
      var settings = {};

      this.$themeSettings.each(function (idx, input) {
        var $input = $(input),
            name = $input.attr('name');

        if ($input.data('sync')) {
          settings[name] = this.$layout.hasClass(name);
        }
      }.bind(this));

      this.changeThemeSettings(settings);

      return this;
    },
    changeThemeSettings: function changeThemeSettings(settings) {
      $.each(settings, function (name, state) {
        var $input = this.getThemeSettingsBy(name);
        $input.prop('checked', state).trigger('change');
      }.bind(this));

      return this;
    },
    getThemeSettingsBy: function getThemeSettingsBy(name) {
      return this.$themeSettings.filter("[name='" + name + "']");
    },
    isHeaderStatic: function isHeaderStatic() {
      return !this.$layout.hasClass(this.CssClasses.LAYOUT_HEADER_FIXED);
    },
    setHeaderFixed: function setHeaderFixed(state) {
      var settings = {};

      this.$layout.toggleClass(this.CssClasses.LAYOUT_HEADER_FIXED, state);

      if (this.isHeaderStatic() && this.isSidebarFixed()) {
        settings[this.CssClasses.LAYOUT_SIDEBAR_FIXED] = state;
      }

      if (this.isHeaderStatic() && this.isSidebarSticky()) {
        settings[this.CssClasses.LAYOUT_SIDEBAR_STICKY] = state;
      }
      this.changeThemeSettings(settings);
    },
    isSidebarFixed: function isSidebarFixed() {
      return this.$layout.hasClass(this.CssClasses.LAYOUT_SIDEBAR_FIXED);
    },
    setSidebarFixed: function setSidebarFixed(state) {
      var settings = {},
          $sidebar = this.getSidebarScrollableArea();

      this.$layout.toggleClass(this.CssClasses.LAYOUT_SIDEBAR_FIXED, state);

      if (!this.isSidebarFixed()) {
        return this.removeCustomScrollbarFrom($sidebar);
      }

      if (this.isHeaderStatic()) {
        settings[this.CssClasses.LAYOUT_HEADER_FIXED] = state;
      }

      if (this.isSidebarSticky()) {
        settings[this.CssClasses.LAYOUT_SIDEBAR_STICKY] = !state;
      }
      this.changeThemeSettings(settings).addCustomScrollbarTo($sidebar);
    },
    isSidebarSticky: function isSidebarSticky() {
      return this.$layout.hasClass(this.CssClasses.LAYOUT_SIDEBAR_STICKY);
    },
    setSidebarSticky: function setSidebarSticky(state) {
      var settings = {};

      this.$layout.toggleClass(this.CssClasses.LAYOUT_SIDEBAR_STICKY, state);

      if (!this.isSidebarSticky()) {
        return this.destroyStickySidebar();
      }

      if (this.isHeaderStatic()) {
        settings[this.CssClasses.LAYOUT_HEADER_FIXED] = state;
      }

      if (this.isSidebarFixed()) {
        settings[this.CssClasses.LAYOUT_SIDEBAR_FIXED] = !state;
      }
      this.changeThemeSettings(settings).createStickySidebar();
    },
    setFooterFixed: function setFooterFixed(state) {
      this.$layout.toggleClass(this.CssClasses.LAYOUT_FOOTER_FIXED, state);
    },
    addCustomScrollbarTo: function addCustomScrollbarTo($el) {
      var options = this.getCustomScrollbarOptions();
      $el.slimScroll(options);
    },
    removeCustomScrollbarFrom: function removeCustomScrollbarFrom($el) {
      var options = this.getCustomScrollbarOptions();

      options.destroy = true;

      $el.slimScroll(options).off().removeAttr('style');
    },
    createStickySidebar: function createStickySidebar() {
      var $target = this.getSidebarScrollableArea(),
          options = this.getStickyOptions();

      options.stickTo = this.$content;

      $target.hcSticky(options).hcSticky('reinit');
    },
    updateStickySidebar: function updateStickySidebar() {
      var $target = this.getSidebarScrollableArea();
      $target.hcSticky('reinit');
    },
    destroyStickySidebar: function destroyStickySidebar() {
      var $target = this.getSidebarScrollableArea();

      $target.data('hcSticky') && $target.hcSticky('destroy').off().removeAttr('style');
    },
    mediaQueryMatches: function mediaQueryMatches() {
      return this.mediaQueryList.matches;
    },
    getSidebarScrollableArea: function getSidebarScrollableArea() {
      return this.$sidebar.find('.' + this.CssClasses.CUSTOM_SCROLLBAR);
    },
    getCreateOptions: function getCreateOptions(prefix) {
      var regex = new RegExp('^' + prefix + '(_)?', 'i'),
          options = {};

      $.each(this.Options, function (key, val) {
        if (regex.test(key)) {
          key = key.replace(regex, '').replace(/_/g, '-');
          key = $.camelCase(key.toLowerCase());
          options[key] = val;
        }
      });

      return options;
    },
    getCustomScrollbarOptions: function getCustomScrollbarOptions() {
      return this.getCreateOptions('custom_scrollbar');
    },
    getSelect2Options: function getSelect2Options() {
      return this.getCreateOptions('select2');
    },
    getSidenavOptions: function getSidenavOptions() {
      return this.getCreateOptions('sidenav');
    },
    getStickyOptions: function getStickyOptions() {
      return this.getCreateOptions('sticky');
    },
    getSortableOptions: function getSortableOptions() {
      return this.getCreateOptions('sortable');
    },
    getBlockUIOptions: function getBlockUIOptions() {
      var options = {},
          $spinner = $(document.createElement('div'));

      $spinner.addClass(this.CssClasses.SPINNER).addClass(this.CssClasses.SPINNER_PRIMARY);

      options.message = $spinner;
      options.css = this.getCreateOptions('block_ui_css');
      options.overlayCSS = this.getCreateOptions('block_ui_overlay_css');

      return options;
    },
    initPlugins: function initPlugins() {
      this.initPeity();
      this.matchHeight();
      this.metisMenu();
      this.select2();
      this.tooltip();
      this.vectorMap();

      return this;
    },
    initPeity: function initPeity() {
      $('[data-peity]').each(function () {
        var data = $(this).data(),
            type = $.camelCase(data.peity);

        $(this).peity(type, data);
      });
    },
    matchHeight: function matchHeight() {
      $('[data-toggle="match-height"]').matchHeight();
    },
    metisMenu: function metisMenu() {
      var options = this.getSidenavOptions();
      this.$sidenav.metisMenu(options);
    },
    select2: function select2() {
      var Select2 = $.fn.select2,
          options = this.getSelect2Options();

      $.each(options, function (key, value) {
        Select2.defaults.set(key, value);
      });
    },
    tooltip: function tooltip() {
      $('[data-toggle="tooltip"]').tooltip();
    },
    vectorMap: function vectorMap() {
      $('[data-toggle="vector-map"]').each(function () {
        var $map = $(this),
            options = $map.data();

        $map.vectorMap(options);
      });
    }
  };

  App.init();
})(jQuery);
