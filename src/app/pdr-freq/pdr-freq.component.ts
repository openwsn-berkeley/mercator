import { Component, OnInit } from '@angular/core';
import { Http, Response } from '@angular/http';
import {ActivatedRoute} from "@angular/router";
declare var jQuery:any;
import { GithubService } from '../github.service';
import {Observable} from 'rxjs/Observable';
declare var CanvasJS: any;

@Component({
  selector: 'app-pdr-freq',
  templateUrl: './pdr-freq.component.html',
  styleUrls: ['./pdr-freq.component.css']
})

export class PdrFreqComponent implements OnInit {

  name: string;
  sites: string[];
  site = "";
  exps: string[];
  macs = [];

  public barChartOptions: any = {
    scaleShowVerticalLines: false,
    responsive: true
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
    this.name = "test";


    this.gith = gith;

    this.route.params.subscribe(params => {

      let site = params['city']
      this.site = site;
      let exp = params['pdr']
      this.barChartData[0]['label'] = exp
      this.gith.getMacs(site, 'pdr_freq', exp).subscribe((res: any) => {
        //console.log(res)
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

  /*
   readCSV(mac){

   console.log(mac,"ACA");

   }*/

  processData(allText) {
    var allLinesArray = allText.split('\n');
    if (allLinesArray.length > 0) {
      var dataPoints = [];
      let barChartLabels = [];
      let barChartData = [];
      for (var i = 1; i <= allLinesArray.length - 1; i++) {
        var rowData = allLinesArray[i].split(',');
        console.log(rowData);
        if (rowData && rowData.length > 1) {
          barChartLabels.push(rowData[0]);
          barChartData.push(rowData[1]);

        }
        //dataPoints.push({ label: rowData[0], y: parseInt(rowData[1]) });


      }
      return [barChartLabels, barChartData]

    }
  }


  readCSV(mac) {
    this.route.params.subscribe(params => {
      let site = params['city']
      let exp = params['pdr']
      let barChartData = this.barChartData;


      this.gith.download_url("https://raw.githubusercontent.com/openwsn-berkeley/mercator/develop/datasets/processed/" + site + "/pdr_freq/" + exp + "/" + mac).subscribe((res: any) => {
        console.log(res)
        let data = this.processData(res);
        this.barChartLabels = data[0];
        this.barChartData[0]['data'] = data[1];
        let clone = JSON.parse(JSON.stringify(this.barChartData));

        this.barChartData = clone;

        console.log(this.barChartData);

        //this.macs = res;

      });
    })
  }
}


