import { FilterOptions } from '@/classes/logs/filters/manager';
import { LogList } from '@/services/list.service';
import { FilterManager } from '@/services/filter_manager.service';
import { Component, OnInit } from '@angular/core';
import { AttributeManager } from '@/services/extractor_manager.service';


@Component({
  selector: 'test-card',
  templateUrl: './test-card.component.html',
  styleUrls: ['./test-card.component.css']
})
export class TestCardComponent implements OnInit {
  filter_opts: FilterOptions
  ids: any = []
  extracts: any = []

  constructor(
    private log_list: LogList,
    private ftr_mgr: FilterManager,
    private attr_mgr: AttributeManager,
  ) {
    this.filter_opts = {}
    this.filter_opts[FilterManager.cats.AGE] = [30]
    this.filter_opts[FilterManager.cats.TYPE] = ["Grindfest"]
  }

  ngOnInit(): void {
    this.log_list.fetch().subscribe()

    this.ftr_mgr.get_add$(this.filter_opts).subscribe(
      data => {
        console.log('filter got', data)
        this.ids.push(data.start)

        this.attr_mgr.extract([data.start], AttributeManager.extrs.EQ).subscribe(
          extr => {
            console.log('extr got', extr)
            this.extracts.push(extr)
          }  
        )
      }
    )
  }

  /* DEBUG */
  get debug() {
    return [
      JSON.stringify(this.ids),
      JSON.stringify(this.extracts, null, 2),
    ]
  }
}
