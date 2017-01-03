import { Component, OnInit } from '@angular/core';
import { Http, Response } from '@angular/http';
import {ActivatedRoute} from "@angular/router";
import { GithubService } from '../github.service';
import {Observable} from 'rxjs/Observable';

@Component({
  selector: 'app-barchart',
  templateUrl: './barchart.component.html',
  styleUrls: ['./barchart.component.css']
})

export class BarChartComponent implements OnInit {

  name: string;
  sites: string[];
  site = "";
  exps: string[];
  macs = [];

  public barChartOptions: any = {
    scaleShowVerticalLines: false,
    responsive: true,
  };
  public barChartLabels: string[] = [];
  public barChartType: string = 'bar';
  public barChartLegend: boolean = true;

  barChartData = [
    {data: [], label: ''},
  ];

  // events
  public chartClicked(e: any): void {
    //console.log(e);
  }

  public chartHovered(e: any): void {
    //console.log(e);
  }


  constructor(private route: ActivatedRoute, private gith: GithubService) {

    this.route.params.subscribe(params => {

      let site = params['city'];
      this.site = site;
      let exp = params['exp'];
      let x2x = params['x2x'];
      this.barChartData[0]['label'] = exp;

      if (params['mac']){
        this.readJSON(params['mac'])
      }

      this.gith.getMacs(site, exp, x2x).subscribe((res: any) => {
        this.macs = res;
      });

    });
  }

  ngOnInit() {
  }

  getExps(site) {
    this.gith.getExps(site).subscribe((res: any) => {
      var localexp = [];
      res.forEach(function (item) {
        localexp.push(item.name);
      });
      this.exps = localexp;
    });
  }

  readJSON(mac) {
    this.route.params.subscribe(params => {
      let site = params['city'];
      let exp = params['exp'];
      let x2x = params['x2x'];
      let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/develop/datasets/processed/";
      this.gith.download_url( url + "/" + site + "/" + exp + "/" + x2x + "/" + mac + "?ref=develop").subscribe((res: any) => {
          this.barChartLabels = res.x;
          this.barChartData = [{data: res.y, label:res.ytitle}];
      });
    })
  }
}


