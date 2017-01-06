import {Component, OnChanges, Input} from '@angular/core';
import { GithubService } from '../github.service';

@Component({
  selector: 'app-barchart',
  templateUrl: './barchart.component.html',
  styleUrls: ['./barchart.component.css']
})

export class BarChartComponent implements OnChanges {

  @Input() input_url;

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

  load_graph() {
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/develop/datasets/processed/";
    if (this.input_url != "") {
      this.gith.download_url(url + this.input_url).subscribe((res: any) => {
        this.barChartLabels = res.x;
        this.barChartData = [{data: res.y, label: res.ytitle}];
      });
    }
  }
}


