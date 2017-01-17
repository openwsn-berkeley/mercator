import { Component, OnInit } from '@angular/core';
import {GithubService} from "../github.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-dataset-selector',
  templateUrl: './dataset-selector.component.html',
  styleUrls: ['./dataset-selector.component.css']
})
export class DatasetSelectorComponent implements OnInit {

  dataset_list = []

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

  redirect(site, date) {
    this.router.navigate(["site", site, date]);
  }
}
