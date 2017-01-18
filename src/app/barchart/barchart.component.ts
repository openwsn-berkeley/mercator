import {Component, OnChanges, Input} from '@angular/core';
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

  ngOnChanges(){
    this.load_graph();
  };

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

  constructor(private gith: GithubService) {}

  // events
  public chartClicked(e: any): void {
    //console.log(e);
  }

  public chartHovered(e: any): void {
    //console.log(e);
  }

  load_chart_config(){
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/";
    this.gith.download_url(url +
      this.site + "/" +
      this.date + "/" +
      this.exp + "/" +
      this.exp_type + "/" +
      "chart_config.json"
    ).subscribe((res: any) => {
      this.barChartOptions = res.ChartOptions;
      console.log(res.ChartOptions)
    });
  }

  load_graph() {
    this.load_chart_config();
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/datasets/processed/";
    this.barChartData = [{data: [], label: ''}];
    if (this.exp_type == "one_to_one") {
      if (this.dst_mac_list.length > 0) {
        for (let i = 0; i < this.dst_mac_list.length; i++) {
          let url_args = [this.site, this.date, this.exp, this.exp_type, this.src_mac, this.dst_mac_list[i]];
          if (this.exp == "pdr_time"){
            this.gith.getFiles(url_args.join('/')).subscribe((res: any) => {
              res.forEach((f) =>{
                this.gith.download_url(url + url_args.join('/') + "/" + f.name).subscribe((res: any) => {
                  this.barChartLabels = res.x;
                  this.barChartData.push({data: res.y, label: res.ytitle});
                });
              });
            });
          } else {
            this.gith.download_url(url + url_args.join('/') + ".json").subscribe((res: any) => {
              this.barChartLabels = res.x;
              this.barChartData.push({data: res.y, label: res.ytitle});
            });
          }
        }
      }
    } else if (this.exp_type == "many_to_many"){
      this.gith.download_url(url +
          this.site + "/"+
          this.date + "/" +
          this.exp + "/" +
          this.exp + ".json"
        ).subscribe((res: any) => {
        this.barChartLabels = res.x;
        this.barChartData.push({data: res.y, label: res.ytitle});
        console.log(this.barChartData)
      });
    }
  }
}


