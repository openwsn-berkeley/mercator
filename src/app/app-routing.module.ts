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
import {DatasetSelectorComponent} from "./dataset-selector/dataset-selector.component";



const routes: Routes = [
  { path: '', pathMatch: 'full', component: IndexComponent  },
  { path: 'site/:site', component: MotemapComponent  },
  { path: 'datasets', component: DatasetSelectorComponent  }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
