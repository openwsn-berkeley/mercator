'use strict';

(function ($) {
  'use strict';

  var LandingPage = {
    Constants: {
      SCROLL_ANIMATION_OFFSET: '85%',
      SCROLL_COUNT_UP_OFFSET: '100%',
      IMAGES_LOADED_BACKGROUND: true
    },
    CssClasses: {
      PAGE_LOADED: 'page-loaded'
    },
    init: function init() {
      this.$body = $(document.body);

      this.getImagesLoadingState().always(function (instance) {
        document.body.className = this.CssClasses.PAGE_LOADED;
      }.bind(this));

      $('[data-toggle="popover"]').popover();

      this.createScrollAnimation().createScrollCountUp();
    },
    getImagesLoadingState: function getImagesLoadingState() {
      return this.$body.imagesLoaded({
        background: this.Constants.IMAGES_LOADED_BACKGROUND
      });
    },
    createScrollAnimation: function createScrollAnimation() {
      var options = {};
      options.offset = this.Constants.SCROLL_ANIMATION_OFFSET;
      options.handler = this.scrollAnimationHandler;

      $('[data-animation-name]').waypoint(options);

      return this;
    },
    scrollAnimationHandler: function scrollAnimationHandler(direction) {
      var $element = $(this.element),
          cssClasses = ['animated'],
          match;

      $.each($element.data(), function (key, val) {
        if (match = /(name|duration|delay)/i.exec(key)) {
          key = match[0].toLowerCase();
          val = key === 'name' ? val : key.concat('-', val);
          cssClasses.push(val);
        }
      });

      $element.removeAttr('data-animation-name').removeAttr('data-animation-duration').removeAttr('data-animation-delay').addClass(cssClasses.join(' '));

      var removeCssClasses = function removeCssClasses() {
        $element.removeClass(cssClasses.join(' '));
      };

      $.support.animation ? $element.one('bsAnimationEnd', removeCssClasses) : removeCssClasses();

      this.destroy();
    },
    createScrollCountUp: function createScrollCountUp() {
      var options = {};
      options.offset = this.Constants.SCROLL_COUNT_UP_OFFSET;
      options.handler = this.scrollCountUpHandler;

      $('[data-count]').waypoint(options);

      return this;
    },
    scrollCountUpHandler: function scrollCountUpHandler(direction) {
      var $element = $(this.element),
          counter,
          startVal,
          endVal;

      startVal = $element.data('startValue');
      endVal = $element.data('endValue');

      counter = new CountUp($element[0], startVal, endVal);
      counter.start();

      this.destroy();
    }
  };

  LandingPage.init();
})(jQuery);
