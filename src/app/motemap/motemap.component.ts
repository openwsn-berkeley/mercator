import { Component, ViewChild } from '@angular/core';
import {AfterViewInit} from "@angular/core";
import {GithubService} from "../github.service";

@Component({
  selector: 'app-motemap',
  templateUrl: './motemap.component.html',
  styleUrls: ['./motemap.component.css']
})
export class MotemapComponent implements AfterViewInit {
  context:CanvasRenderingContext2D;

  circles = [];
  src_mac = "";
  input_url = "";

  @ViewChild("myCanvas") myCanvas;

  constructor(private gith:GithubService){
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/develop/metas/locations.json";
    let newcircles = [];
    this.gith.download_url(url).subscribe((res: any) => {
      res.forEach( function(item){
        if (item.location == "strasbourg") {
          item.nodes.forEach( function(node){
            if (node.mac) {
              newcircles.push({x: node.x, y: node.y, msg: node.mac, color: "black"});
            }
          });
        }
      });
    });
    this.circles = newcircles;
  }

  ngAfterViewInit() { }

  boom(circle_id, msg){
    this.src_mac = msg;
    this.circles.forEach(function(item){
      item.color = "black";
    });
    this.circles[circle_id].color = "red";
    this.input_url = "strasbourg/pdr_freq/one_to_many/" + msg + ".json";
  }
}
