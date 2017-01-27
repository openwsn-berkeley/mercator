import {Component, OnChanges, Input, SimpleChanges} from '@angular/core';
import { GithubService } from '../github.service';
import {Observable} from "rxjs";

@Component({
  selector: 'app-barchart',
  templateUrl: './barchart.component.html',
  styleUrls: ['./barchart.component.css']
})

export class BarChartComponent implements OnChanges {

  @Input() site;
  @Input() date;
  @Input() exp;
  @Input() exp_type;
  @Input() src_mac;
  @Input() dst_mac_list;

  result = {};

  public barChartOptions: any = {
    responsive: true,
    animation : false,
    scales: {},
  };
  public chartLabelsList: string[][] = [[]];
  public barChartType: string = 'bar';
  public barChartLegend: boolean = true;

  chartDataList = [];

  constructor(private gith: GithubService) {
  }

  ngOnChanges(changes: SimpleChanges){
    if (
      ("exp_type" in changes &&
      changes["exp_type"].currentValue != undefined &&
      changes["exp_type"].currentValue != "") ||
      ("exp" in changes &&
      changes["exp"].currentValue != undefined &&
      changes["exp"].currentValue != "")
    ) {
        this.load_chart_config();
    }
    this.load_graph();
  };

  // events
  public chartClicked(e: any): void {
    //console.log(e);
  }

  public chartHovered(e: any): void {
    //console.log(e);
  }

  reload_chart(){
    this.chartDataList = [];
    if (
      this.barChartOptions.scales.xAxes != undefined &&
      this.barChartOptions.scales.xAxes[0].type != undefined &&
      this.barChartOptions.scales.xAxes[0].type == "linear")
    {
      for (let key in this.result) {
        for (let i = 0; i < this.result[key].length; i++) {
          if (this.result[key][i].x.length > 0) {
            // format graph data
            let data_list = [];
            for (let j = 0; j < this.result[key][i].x.length; j++) {
              data_list.push({x: this.result[key][i].x[j], y: this.result[key][i].y[j]});
            }
            this.chartDataList.push([{data: data_list, label: this.result[key][i].label}]);
          }
        }
      }
    } else {
      let c = 0;
      for (let key in this.result) {
        this.chartDataList[c] = [];
        this.chartLabelsList[c] = [];
        for (let i = 0; i < this.result[key].length; i++) {
          this.chartDataList[c].push({
            data: this.result[key][i].y,
            label: this.result[key][i].label
          });
          this.chartLabelsList[c] = this.result[key][i].x;
        }
        c++;
      }
    }
  }

  load_chart_config(){
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/";
    let url_args = [this.site, this.date, this.exp, this.exp_type];
    this.gith.download_url(url + url_args.join("/") + "/" + "chart_config.json").subscribe(
      (res) => {
        this.barChartOptions = Object.assign({}, this.barChartOptions, res.ChartOptions);
        this.barChartType = res.ChartType;
        this.reload_chart()
      },
      (error) => {console.log("Can not find chart option file."), this.reload_chart()}
    );
  }

  load_graph() {
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/";
    let url_args = [this.site, this.date, this.exp, this.exp_type];

    this.result = {};
    if (this.exp_type == "one_to_one") {
      let observArray = [];
      for (let i = 0; i < this.dst_mac_list.length; i++) {
        let url_args_full = url_args.concat(this.src_mac, this.dst_mac_list[i]);
        if (this.exp.split("_").length == 3){
          this.gith.getFiles(url_args_full.join('/')).subscribe((file_list: any) => {
            file_list.forEach((file) =>{
              observArray.push(this.gith.download_url(url + url_args_full.join('/') + "/" + file.name))
            });
            Observable.forkJoin(observArray).subscribe((contentList: any) => {
              contentList.forEach((fileContent) => {
                if (!(this.src_mac in this.result)){this.result[this.src_mac] = []}
                this.result[this.src_mac].push(fileContent);
              });
              this.reload_chart();
            });
          });
        } else {
          observArray.push(this.gith.download_url(url + url_args_full.join('/') + ".json"));
        }
      }
      Observable.forkJoin(observArray).subscribe((contentList: any) => {
        contentList.forEach((fileContent) => {
          if (!(this.src_mac in this.result)){this.result[this.src_mac] = []}
          this.result[this.src_mac].push(fileContent);
        });
        this.reload_chart();
      });
    } else if (this.exp_type == "one_to_many") {
      if (this.src_mac != "") {
        let url_args_full = url_args.concat(this.src_mac);
        this.gith.download_url(url + url_args_full.join('/') + ".json").subscribe((res) => {
          this.result[this.src_mac] = [res];
          this.reload_chart();
        });
      }
    } else if (this.exp_type == "many_to_many"){
      this.gith.download_url(url + url_args.join("/") + "/" + this.exp + ".json"
        ).subscribe((res) => {
            this.result[this.exp] = [res];
            this.reload_chart()
          }
      );
    }
    this.reload_chart()
  }
}


