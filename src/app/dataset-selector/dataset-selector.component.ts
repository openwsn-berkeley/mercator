import { Component, OnInit } from '@angular/core';
import {GithubService} from "../github.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-dataset-selector',
  templateUrl: './dataset-selector.component.html',
  styleUrls: ['./dataset-selector.component.css']
})
export class DatasetSelectorComponent implements OnInit {

  dataset_list = [];
  exp_list = [];
  type_list = [];
  curr_site = "";
  curr_date = "";
  curr_exp = "";

  constructor(private gith:GithubService, private router: Router) { }

  ngOnInit() {
    this.gith.getSites().subscribe((res: any) => {
      res.forEach((site) => {
        this.gith.getFiles(site.name).subscribe((res1: any) => {
          res1.forEach((file) => {
            let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/" +
              site.name + "/" + file.name +"/info.json";
            this.gith.download_url(url).subscribe((res2: any) => {
              res2.site=site.name;
              res2.date=file.name;
              this.dataset_list.push(res2);
            });
          });
        });
      });
    });
  }

  get_exp_list(site, date) {
    this.curr_site = site;
    this.curr_date = date;
    this.gith.getExps(site, date).subscribe((res: any) => {
      this.exp_list = [];
      res.forEach((exp) => {
        if (exp.type == "dir") {
          this.exp_list.push(exp.name)
        }
      });
    });
  }

  get_type_list(exp){
    this.curr_exp = exp;
    this.gith.getTypes(this.curr_site, this.curr_date, exp).subscribe((res: any) => {
      this.type_list = [];
      res.forEach((exptype) => {
        if (exptype.type == "dir") {
          this.type_list.push(exptype.name)
        }
      });
    });
  }

  get_graph(exptype){
    this.router.navigate(["motemap", this.curr_site, this.curr_date, this.curr_exp, exptype]);
  }
}
