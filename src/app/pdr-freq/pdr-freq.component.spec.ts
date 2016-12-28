/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { PdrFreqComponent } from './pdr-freq.component';

describe('PdrFreqComponent', () => {
  let component: PdrFreqComponent;
  let fixture: ComponentFixture<PdrFreqComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PdrFreqComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PdrFreqComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
