import { Component, OnInit } from '@angular/core';
import {GithubService} from "../github.service";
import {Router, ActivatedRoute, Params} from "@angular/router";
import {Location} from '@angular/common';

@Component({
  selector: 'app-dataset-selector',
  templateUrl: './dataset-selector.component.html',
  styleUrls: ['./dataset-selector.component.css']
})
export class DatasetSelectorComponent implements OnInit {

  dataset_list;
  exp_list = [];
  site = "";
  date = "";
  exp = "";
  exp_type = "";

  constructor(private gith:GithubService, private router: Router,
              private route: ActivatedRoute, private location: Location) {
    // get route parameters
    this.route.params.subscribe((params: Params) => {
      if ("site" in params) {
        this.site = params['site'];
        if ("date" in params) {
          this.get_exp_list(this.site, params['date']);
          if ("exp" in params) {
            this.set_exp(params['exp']);
          }
        }
        this.exp_list = [];
      }
      this.get_dataset_list();
    });
  }

  ngOnInit() {}

  get_dataset_list(){
    this.dataset_list = [];
    this.gith.getSites().subscribe((res: any) => {
      res.forEach((site) => {
        if (this.site == "" || this.site == site.name) {
          this.gith.getFiles(site.name).subscribe((res1: any) => {
            res1.forEach((file) => {
              let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/" +
                site.name + "/" + file.name + "/info.json";
                this.gith.download_url(url).subscribe((res2: any) => {
                  res2.site = site.name;
                  res2.date = file.name;
                  this.dataset_list.push(res2);
                });
            });
          });
        }
      });
    });
  }

  get_exp_list(site, date) {
    this.site = site;
    this.date = date;
    this.gith.getExps(site, date).subscribe((res: any) => {
      this.exp_list = [];
      res.forEach((exp) => {
        if (exp.type == "dir") {
          this.exp_list.push(exp.name)
        }
      });
    });
    // update url
    this.location.replaceState('/'+ site + '/' + date + '/')
  }

  set_exp(exp){
    this.exp = exp;
    this.exp_type = "many_to_many";
    // update url
    this.location.replaceState('/'+ this.site + '/' + this.date + '/' + exp + '/')
  }
}
