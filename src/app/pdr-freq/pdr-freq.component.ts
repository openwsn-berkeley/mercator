import { Component, OnInit } from '@angular/core';
import { Http, Response } from '@angular/http';
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
  exps: string[];
  macs: string[];

  constructor(private gith:GithubService) {
    this.name = "test";

    // get site names
    this.gith.getSites().subscribe((res: any) => {
            var localsites = [];
            res.forEach( function(item){ localsites.push(item.name); });
            this.sites = localsites;
            });
  }

  ngOnInit() {}

  getExps(site) {
      this.gith.getExps(site).subscribe((res: any) => {
        var localexp = [];
        res.forEach( function(item){ localexp.push(item.name); });
        this.exps = localexp;
        });
  }
  getMacs(site,exp) {
      this.gith.getMacs(site,exp).subscribe((res: any) => {
        var localmacs = [];
        res.forEach( function(item){ localmacs.push(item.name); });
        this.macs = localmacs;
        });
  }

  readCSV(site,exp,mac){
    jQuery.ajax({
        type: "GET",
        url: "https://raw.githubusercontent.com/openwsn-berkeley/mercator/develop/datasets/processed/"+site+"/"+exp+"/"+mac,
        dataType: "text",
        success: function (data) { processData(data); }
    });

    function processData(allText) {
        var allLinesArray = allText.split('\n');
        if (allLinesArray.length > 0) {
            var dataPoints = [];
            for (var i = 1; i <= allLinesArray.length - 1; i++) {
                var rowData = allLinesArray[i].split(',');
                if(rowData && rowData.length > 1)
                    dataPoints.push({ label: rowData[0], y: parseInt(rowData[1]) });
            }
            chart.options.data[0].dataPoints = dataPoints;
            chart.render();
        }
    }

    var chart = new CanvasJS.Chart("chartContainer",
    {
        animationEnabled: true,
        theme: "theme2",
        //exportEnabled: true,
        title:{
            text: "Simple Column Chart"
        },
        data: [
        {
            type: "column",
            dataPoints: [
            ]
        }
        ]
    });

    chart.render();
  }
}
