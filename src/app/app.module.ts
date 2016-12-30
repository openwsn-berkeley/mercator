import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { GithubService } from './github.service';

import { AppComponent } from './app.component';
import { PdrFreqComponent } from './pdr-freq/pdr-freq.component';
import { AppRoutingModule }     from './app-routing.module';
import { IndexComponent } from './index/index.component';
import { PdrComponent } from './pdr/pdr.component';

import { ChartsModule } from 'ng2-charts/ng2-charts';




@NgModule({
  declarations: [
    AppComponent,
    PdrFreqComponent,
    IndexComponent,
    PdrComponent
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
