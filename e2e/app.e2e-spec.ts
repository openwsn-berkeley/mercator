import { MercatorPage } from './app.po';

describe('mercator App', function() {
  let page: MercatorPage;

  beforeEach(() => {
    page = new MercatorPage();
  });

  it('should display message saying app works', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('app works!');
  });
});
