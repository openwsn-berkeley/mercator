import {Component, OnChanges, Input, SimpleChanges} from '@angular/core';
import { GithubService } from '../github.service';

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

  result = [];

  public barChartOptions: any = {
    responsive: true,
    scales: {},
  };
  public barChartLabels: string[] = [];
  public barChartType: string = 'bar';
  public barChartLegend: boolean = true;

  barChartData = [{data: [], label: ''}];

  constructor(private gith: GithubService) {

  }

  ngOnChanges(changes: SimpleChanges){
    if ("exp_type" in changes) {
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
    this.barChartData = [{data: [], label: ''}];
    if (this.barChartOptions.scales.xAxes != undefined &&
        this.barChartOptions.scales.xAxes[0].type == "linear")
    {
      this.result.forEach((item) => {
        if (item.x.length > 0) {
          // format graph data
          let data_list = [];
          for (let i = 0; i < item.x.length; i++) {
            data_list.push({x: item.x[i], y: item.y[i]});
          }
          this.barChartData.push({data: data_list, label: item.ytitle + " over " + item.xtitle});
        }
      })
    } else {
      this.result.forEach((item) => {
        this.barChartData.push({data: item.y, label: item.ytitle + " over " + item.xtitle});
        this.barChartLabels = item.x;
      })
    }
  }

  load_chart_config(){
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/";
    let url_args = [this.site, this.date, this.exp, this.exp_type];
    this.gith.download_url(url + url_args.join("/") + "/" + "chart_config.json").subscribe(
      (res) => {
        this.barChartOptions = Object.assign({}, this.barChartOptions, res.ChartOptions);
        this.barChartType = res.ChartType;
      },
      (error) => {console.log("Can not find chart option file.")}
    );
  }

  load_graph() {
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/";
    let url_args = [this.site, this.date, this.exp, this.exp_type];

    this.result = [];
    if (this.exp_type == "one_to_one") {
      for (let i = 0; i < this.dst_mac_list.length; i++) {
        let url_args_full = url_args.concat(this.src_mac, this.dst_mac_list[i]);
        if (this.exp == "pdr_time"){
          this.gith.getFiles(url_args_full.join('/')).subscribe((res: any) => {
            res.forEach((f) =>{
              this.result.push(res);
            });
            this.reload_chart();
            console.log("test")
          });
        } else {
          this.gith.download_url(url + url_args_full.join('/') + ".json").subscribe((res: any) => {
            this.result.push(res);
            this.reload_chart();
            console.log("test")
          });
        }
      }
    } else if (this.exp_type == "one_to_many") {
      if (this.src_mac != "") {
        let url_args_full = url_args.concat(this.src_mac);
        this.gith.download_url(url + url_args_full.join('/') + ".json").subscribe((res) => {
          this.result.push(res);
          this.reload_chart();
        });
      }
    } else if (this.exp_type == "many_to_many"){
      this.gith.download_url(url + url_args.join("/") + "/" + this.exp + ".json"
        ).subscribe((res: any) => {
          this.result.push(res);
          this.reload_chart();
      });
    }
  }
}


