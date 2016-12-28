import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { GithubService } from './github.service';

import { AppComponent } from './app.component';
import { PdrFreqComponent } from './pdr-freq/pdr-freq.component';

@NgModule({
  declarations: [
    AppComponent,
    PdrFreqComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule
  ],
  providers: [GithubService],
  bootstrap: [AppComponent]
})
export class AppModule { }
