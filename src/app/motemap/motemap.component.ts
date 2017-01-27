import {Component, ViewChild, Input, SimpleChanges} from '@angular/core';
import {AfterViewInit} from "@angular/core";
import {GithubService} from "../github.service";
import {ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-motemap',
  templateUrl: './motemap.component.html',
  styleUrls: ['./motemap.component.css']
})


export class MotemapComponent implements AfterViewInit {

  @Input() site;
  @Input() date;
  @Input() exp;
  exp_type: string;

  context:CanvasRenderingContext2D;

  circles = [];
  src_mac = "";
  dst_mac_list = [];

  @ViewChild("myCanvas") myCanvas;

  COLOR_ENABLED = "black";
  COLOR_DISABLED = "grey";

  constructor(private gith:GithubService) {}

  ngOnChanges(changes: SimpleChanges) {
    if ("site" in changes){
      this.draw_nodes();
    }
    if ("exp" in changes){
      this.src_mac = "";
      this.dst_mac_list = [];
      this.exp_type = "many_to_many"
      this.circles.forEach((item) => {
        item.color = this.COLOR_ENABLED;
      });
    }
  }

  ngAfterViewInit() { }

  draw_nodes(){
    let newcircles = [];
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/metas/"+this.site+".json";

    this.gith.download_url(url).subscribe((res: any) => {
      res.forEach((node) => {
        if (node.mac) {
          newcircles.push({x: node.x, y: node.y, msg: node.mac, color: this.COLOR_DISABLED});
        }
      });
    });
    this.circles = newcircles;
  }

  node_clicked(circle_id, msg) {
    if (this.src_mac == "") {
      // new src mac
      this.src_mac = msg;
      this.circles.forEach((item) => {
        item.color = this.COLOR_ENABLED;
      });
      this.circles[circle_id].color = "red";
      this.exp_type = "one_to_many";
    } else if (this.src_mac == msg) {
      // cancel src mac
      this.circles.forEach((item) => {
        item.color = this.COLOR_ENABLED;
      });
      this.dst_mac_list = [];
      this.src_mac = "";
      this.exp_type = "many_to_many";
    } else {
      let found = -1;
      for (let i=this.dst_mac_list.length-1; i>=0; i--) {
        if (this.dst_mac_list[i] === msg) {
          found = i;
          break;
        }
      }
      if (found != -1){
          // cancel dst_mac
          this.dst_mac_list.splice(found, 1);
          this.circles[circle_id].color = this.COLOR_ENABLED;
      } else {
        // new dst_mac
        this.dst_mac_list.push(msg);
        this.circles[circle_id].color = "green";
      }
      this.dst_mac_list = this.dst_mac_list.slice(); // update reference
      this.exp_type = "one_to_one";
    }
  }
}
