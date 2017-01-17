/**
 * Created by malba on 30-12-16.
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { MotemapComponent } from './motemap/motemap.component';
import {DatasetSelectorComponent} from "./dataset-selector/dataset-selector.component";



const routes: Routes = [
  { path: '', pathMatch: 'full', component: DatasetSelectorComponent  },
  { path: 'o2o/:site/:date/:exp', component: MotemapComponent  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
