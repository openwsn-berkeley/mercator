'use strict';

(function ($) {
  'use strict';

  var Mail = {
    Constants: {
      MEDIA_QUERY_BREAKPOINT: '992px'
    },
    CssClasses: {
      MAIL_LIST: 'mail-list',
      MAIL_LIST_ITEM: 'mail-list-item',
      MAIL_LIST_LINK: 'mail-list-link',
      MAIL_CONTENT: 'mail-content',
      ACTIVE: 'active',
      HOVER: 'hover'
    },
    init: function init() {
      this.$window = $(window);
      this.$list = $('.' + this.CssClasses.MAIL_LIST);
      this.$items = $('.' + this.CssClasses.MAIL_LIST_ITEM);
      this.$links = $('.' + this.CssClasses.MAIL_LIST_LINK);
      this.$content = $('.' + this.CssClasses.MAIL_CONTENT);
      this.$backBtns = this.$content.find('[data-toggle="tab"]');
      this.breakpoint = null;

      this.bindEvents();
    },
    bindEvents: function bindEvents() {
      this.$items.on('mouseenter.e.mail', this.handleItemMouseEnter.bind(this));
      this.$items.on('mouseleave.e.mail', this.handleItemMouseLeave.bind(this));

      this.$links.on('click.e.mail', this.handleLinkClick.bind(this));
      this.$links.add(this.$backBtns).on('shown.bs.tab', this.handleTabShown.bind(this));

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
          $item = $link.closest('.' + this.CssClasses.MAIL_LIST_ITEM);

      if ($item.hasClass(this.CssClasses.ACTIVE)) $item.removeClass(this.CssClasses.ACTIVE);

      this.rememberScrollbarPos();
    },
    handleTabShown: function handleTabShown(evt) {
      var $trigger = $(evt.currentTarget),
          $activeLink = this.getActiveLink();

      if (!$trigger.is($activeLink)) {
        this.scrollTo(this.rememberedScrollbarPos());
      } else {
        this.scrollTo(0);
      }
    },
    handleMediaQueryChange: function handleMediaQueryChange(evt) {
      var $target = this[this.mediaQueryMatches() ? 'getBackBtn' : 'getActiveLink']();

      $target.length && $target.trigger('click');
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
    getActiveMail: function getActiveMail() {
      return this.$content.filter('.' + this.CssClasses.ACTIVE);
    },
    getActiveLink: function getActiveLink() {
      var $activeItem = this.getActiveItem();
      return $activeItem.find('[data-toggle="tab"]');
    },
    getBackBtn: function getBackBtn() {
      var $activeMail = this.getActiveMail();
      return $activeMail.find('[data-toggle="tab"]');
    },
    scrollTo: function scrollTo(ypos) {
      this.$window.scrollTop(ypos);
    }
  };

  Mail.init();
})(jQuery);
