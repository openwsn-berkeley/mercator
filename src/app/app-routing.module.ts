/**
 * Created by malba on 30-12-16.
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { BarChartComponent } from './barchart/barchart.component';
import { IndexComponent } from './index/index.component';

import { PdrComponent } from './pdr/pdr.component';
import { MotemapComponent } from './motemap/motemap.component';



const routes: Routes = [
  { path: '', component: MotemapComponent  },
  { path: 'motemap', component: MotemapComponent  },
  { path: 'city/:city/pdr',  component: PdrComponent },
  { path: 'city/pdr/:pdr', component: BarChartComponent },
  { path: ':city/:exp/:x2x',  component: BarChartComponent },
  { path: ':city/:exp/:x2x/:mac',  component: BarChartComponent }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
