'use strict';

(function ($) {
  'use strict';

  var Profile = {
    Constants: {
      // None for now.
    },
    CssClasses: {
      FEED: 'feed',
      FEED_ITEM: 'feed-item'
    },
    init: function init() {
      this.$feed = $('.' + this.CssClasses.FEED);
      this.$feedItem = $('.' + this.CssClasses.FEED_ITEM);

      this.createGridLayout();

      this.getImagesLoadingState().always(function (instance) {
        this.updateGridLayout(); // after images are loaded
      }.bind(this));
    },
    getImagesLoadingState: function getImagesLoadingState() {
      return this.$feed.imagesLoaded();
    },
    createGridLayout: function createGridLayout() {
      var options = {};
      options.itemSelector = '.' + this.CssClasses.FEED_ITEM;

      this.$feed.masonry(options);
    },
    updateGridLayout: function updateGridLayout() {
      this.$feed.masonry('layout');
    }
  };

  Profile.init();
})(jQuery);
