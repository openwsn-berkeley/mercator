import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { GithubService } from './github.service';

import { AppComponent } from './app.component';
import { BarChartComponent } from './barchart/barchart.component';
import { AppRoutingModule }     from './app-routing.module';
import { IndexComponent } from './index/index.component';

import { ChartsModule } from 'ng2-charts/ng2-charts';
import { MotemapComponent } from './motemap/motemap.component';
import { DatasetSelectorComponent } from './dataset-selector/dataset-selector.component';

@NgModule({
  declarations: [
    AppComponent,
    BarChartComponent,
    IndexComponent,
    MotemapComponent,
    DatasetSelectorComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    AppRoutingModule,
    ChartsModule
  ],
  providers: [GithubService],
  bootstrap: [AppComponent]
})
export class AppModule  {

}
