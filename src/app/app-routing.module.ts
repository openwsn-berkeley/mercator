/**
 * Created by malba on 30-12-16.
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { PdrFreqComponent } from './pdr-freq/pdr-freq.component';
import { IndexComponent } from './index/index.component';

import { PdrComponent } from './pdr/pdr.component';



const routes: Routes = [
  { path: '', component: IndexComponent  },
  { path: 'city/:city/pdr',  component: PdrComponent },
  { path: 'city/:city/pdr/:pdr',  component: PdrFreqComponent },

];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
