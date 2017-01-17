import { Component, OnInit } from '@angular/core';
import {GithubService} from "../github.service";

@Component({
  selector: 'app-dataset-selector',
  templateUrl: './dataset-selector.component.html',
  styleUrls: ['./dataset-selector.component.css']
})
export class DatasetSelectorComponent implements OnInit {

  dataset_list = []

  constructor(private gith:GithubService) { }

  ngOnInit() {
    this.gith.getSites().subscribe((res: any) => {
      res.forEach((site) => {
        this.gith.getFiles(site.name).subscribe((res1: any) => {
          res1.forEach((file) => {
            let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/" +
              site.name + "/" + file.name +"/info.json";
            this.gith.download_url(url).subscribe((res2: any) => {
              res2.site=site.name;
              res2.data=site.name;
              this.dataset_list.push(res2);
            });
          });
        });
      });
    });
  }
}
