'use strict';

(function ($) {
  "use strict";

  var Messenger = {
    Constants: {
      CUSTOM_SCROLLBAR_ALWAYS_VISIBLE: true,
      CUSTOM_SCROLLBAR_DISTANCE: '4px',
      CUSTOM_SCROLLBAR_HEIGHT: '100%',
      CUSTOM_SCROLLBAR_POSITION: 'right',
      CUSTOM_SCROLLBAR_SIZE: '7px',
      CUSTOM_SCROLLBAR_START: 'bottom',
      CUSTOM_SCROLLBAR_WIDTH: '100%',
      MEDIA_QUERY_BREAKPOINT: '992px'
    },
    CssClasses: {
      LAYOUT: 'layout',
      LAYOUT_HEADER: 'layout-header',

      MESSENGER_LIST: 'messenger-list',
      MESSENGER_LIST_ITEM: 'messenger-list-item',
      MESSENGER_LIST_LINK: 'messenger-list-link',
      MESSENGER_CONTENT: 'messenger-content',
      MESSENGER_SCROLLABLE_CONTENT: 'messenger-scrollable-content',

      CUSTOM_SCROLLBAR: 'messenger-scrollbar',
      CUSTOM_SCROLLBAR_BAR: 'messenger-scrollbar-gripper',
      CUSTOM_SCROLLBAR_RAIL: 'messenger-scrollbar-track',
      CUSTOM_SCROLLBAR_WRAPPER: 'messenger-scrollable-area',

      ACTIVE: 'active',
      HOVER: 'hover'
    },
    KeyCodes: {
      OPEN_SQUARE_BRACKET: 219,
      CLOSE_SQUARE_BRACKET: 221
    },
    init: function init() {
      this.$window = $(window);
      this.$offset = $('.' + this.CssClasses.LAYOUT_HEADER);
      this.$list = $('.' + this.CssClasses.MESSENGER_LIST);
      this.$items = $('.' + this.CssClasses.MESSENGER_LIST_ITEM);
      this.$links = $('.' + this.CssClasses.MESSENGER_LIST_LINK);
      this.$content = $('.' + this.CssClasses.MESSENGER_CONTENT);
      this.$backBtns = this.$content.find('[data-toggle="tab"]');
      this.breakpoint = null;

      this.bindEvents();
    },
    bindEvents: function bindEvents() {
      this.$items.on('mouseenter.e.messenger', this.handleItemMouseEnter.bind(this));
      this.$items.on('mouseleave.e.messenger', this.handleItemMouseLeave.bind(this));

      this.$links.on('click.e.messenger', this.handleLinkClick.bind(this));
      this.$window.on('resize.e.messenger', this.handleWindowResize.bind(this));

      this.$links.add(this.$backBtns).on('shown.bs.tab', this.handleTabShown.bind(this)).on('hidden.bs.tab', this.handleTabHidden.bind(this));

      this.breakpoint = window.matchMedia('(max-width: ' + this.Constants.MEDIA_QUERY_BREAKPOINT + ')');
      this.breakpoint.addListener(this.handleMediaQueryChange.bind(this));
    },
    handleItemMouseEnter: function handleItemMouseEnter(evt) {
      $(evt.currentTarget).addClass(this.CssClasses.HOVER);
    },
    handleItemMouseLeave: function handleItemMouseLeave(evt) {
      $(evt.currentTarget).removeClass(this.CssClasses.HOVER);
    },
    handleLinkClick: function handleLinkClick(evt) {
      var $link = $(evt.currentTarget),
          $item = $link.closest('.' + this.CssClasses.MESSENGER_LIST_ITEM);

      if ($item.hasClass(this.CssClasses.ACTIVE)) $item.removeClass(this.CssClasses.ACTIVE);

      this.rememberScrollbarPos();
    },
    handleWindowResize: function handleWindowResize(evt) {
      this.adjustActiveConversation();
      this.updateCustomScrollBar();
    },
    handleTabShown: function handleTabShown(evt) {
      var $trigger = $(evt.currentTarget),
          $activeLink = this.getActiveLink();

      if ($trigger.is($activeLink)) {
        var $scrollableArea = this.getScrollableArea();

        this.adjustActiveConversation();
        this.addCustomScrollbarTo($scrollableArea);
      } else {
        this.scrollTo(this.rememberedScrollbarPos());
      }
    },
    handleTabHidden: function handleTabHidden(evt) {
      var $trigger = $(evt.currentTarget),
          $prevTab = $($trigger.attr('href')),
          $scrollableArea = $prevTab.find('.' + this.CssClasses.MESSENGER_SCROLLABLE_CONTENT);

      $prevTab.removeAttr('style');
      this.removeCustomScrollbarFrom($scrollableArea);
    },
    handleMediaQueryChange: function handleMediaQueryChange(evt) {
      var $target = this[this.mediaQueryMatches() ? 'getBackBtn' : 'getActiveLink']();

      $target.length && $target.trigger('click');
      this.resetActiveConversation();
    },
    mediaQueryMatches: function mediaQueryMatches() {
      return this.breakpoint.matches;
    },
    rememberScrollbarPos: function rememberScrollbarPos() {
      this.ypos = this.$window.scrollTop();
    },
    rememberedScrollbarPos: function rememberedScrollbarPos() {
      return this.ypos;
    },
    getActiveItem: function getActiveItem() {
      return this.$items.filter('.' + this.CssClasses.ACTIVE);
    },
    getActiveConversation: function getActiveConversation() {
      return this.$content.filter('.' + this.CssClasses.ACTIVE);
    },
    getActiveLink: function getActiveLink() {
      var $activeItem = this.getActiveItem();
      return $activeItem.find('[data-toggle="tab"]');
    },
    getBackBtn: function getBackBtn() {
      var $activeConversation = this.getActiveConversation();
      return $activeConversation.find('[data-toggle="tab"]');
    },
    getScrollableArea: function getScrollableArea() {
      var $activeConversation = this.getActiveConversation();
      return $activeConversation.find('.' + this.CssClasses.MESSENGER_SCROLLABLE_CONTENT);
    },
    adjustActiveConversation: function adjustActiveConversation() {
      var $activeConversation = this.getActiveConversation();

      if (this.mediaQueryMatches() && $activeConversation.length) $activeConversation.height(this.calculateTabHeight());
    },
    resetActiveConversation: function resetActiveConversation() {
      var $activeConversation = this.getActiveConversation();
      $activeConversation.length && $activeConversation.removeAttr('style');
    },
    addCustomScrollbarTo: function addCustomScrollbarTo($el) {
      $el.slimScroll(this.getCustomScrollbarOptions());
    },
    updateCustomScrollBar: function updateCustomScrollBar() {
      var $target = this.getScrollableArea(),
          options = this.getCustomScrollbarOptions();

      $target.slimScroll(options);
    },
    removeCustomScrollbarFrom: function removeCustomScrollbarFrom($el) {
      var options = this.getCustomScrollbarOptions();
      options.destroy = true;

      $el.slimScroll(options).off().removeAttr('style');
    },
    scrollTo: function scrollTo(ypos) {
      this.$window.scrollTop(ypos);
    },
    calculateTabHeight: function calculateTabHeight() {
      var height = this.$window.height(),
          offset = this.$offset.height();

      return height - offset;
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
    getCustomScrollbarOptions: function getCustomScrollbarOptions() {
      return this.getCreateOptions('custom_scrollbar', function (options, prop, key, val) {
        key = prop === 'CssClasses' ? key + 'Class' : key;
        return options[key] = val;
      });
    }
  };

  Messenger.init();
})(jQuery);
