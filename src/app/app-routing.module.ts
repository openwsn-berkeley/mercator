/**
 * Created by malba on 30-12-16.
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import {DatasetSelectorComponent} from "./dataset-selector/dataset-selector.component";
import {IndexComponent} from "./index/index.component";

const routes: Routes = [
  { path: '', pathMatch: 'full', component: IndexComponent  },
  { path: ':site', component: DatasetSelectorComponent  },
  { path: ':site/:date', component: DatasetSelectorComponent  },
  { path: ':site/:date/:exp', component: DatasetSelectorComponent  }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
