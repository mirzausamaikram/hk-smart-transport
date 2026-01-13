<script lang="ts">

  import { createEventDispatcher } from "svelte";

  type Result = { name?: string; address?: string; [key: string]: any };

  export let placeholder: string = "";
  export let value: string = "";

  let results: Result[] = [];
  let timer: number | null = null;
  let highlighted = -1;

  const dispatch = createEventDispatcher();

  function scheduleSearch() {
    if (timer) clearTimeout(timer);
    if (value.length < 2) {
      results = [];
      highlighted = -1;
      return;
    }
    timer = setTimeout(() => doSearch(), 260) as unknown as number;
  }

  async function doSearch() {
    try {
      const q = encodeURIComponent(value.trim());
      const res = await fetch(`http:
      if (!res.ok) {
        results = [];
        return;
      }
      results = await res.json();
      highlighted = -1;
    } catch (e) {
      results = [];
    }
  }

  function choose(r: Result) {
    dispatch("select", r);
    value = r.name || value;
    results = [];
    highlighted = -1;
  }

  function clear() {
    value = "";
    results = [];
    highlighted = -1;
    dispatch('clear');
  }

  function onKey(e: KeyboardEvent) {
    if (!results || results.length === 0) return;
    if (e.key === 'ArrowDown') {
      highlighted = Math.min(highlighted + 1, results.length - 1);
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      highlighted = Math.max(highlighted - 1, 0);
      e.preventDefault();
    } else if (e.key === 'Enter') {
      if (highlighted >= 0 && highlighted < results.length) choose(results[highlighted]);
      e.preventDefault();
    } else if (e.key === 'Escape') {
      results = [];
      highlighted = -1;
    }
  }
</script>

<div class="search-wrapper">
  <div class="input-wrap">
    <svg class="icon search-icon" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M15.5 14h-.79l-.28-.27a6.471 6.471 0 001.57-5.34C15.27 5.59 12.36 3 8.99 3 5.13 3 2 6.13 2 9.99 2 13.86 5.13 17 8.99 17c1.61 0 3.09-.59 4.23-1.57l.27.28v.79L18 20.49 20.49 18l-4.99-4zM8.99 15C6.24 15 4 12.76 4 9.99 4 7.23 6.24 5 8.99 5 11.75 5 13.99 7.23 13.99 9.99 13.99 12.76 11.75 15 8.99 15z"/></svg>

    <input
      class="search-input"
      bind:value={value}
      placeholder={placeholder}
      on:input={scheduleSearch}
      on:keydown={onKey}
      aria-autocomplete="list"
      aria-expanded={results.length > 0}
    />

    {#if value}
      <button class="clear-btn" aria-label="Clear" on:click={clear}>✕</button>
    {/if}
  </div>

  {#if results.length}
    <ul class="dropdown" role="listbox">
      {#each results as r, idx}
        <li role="option" aria-selected={highlighted === idx} class:selected={highlighted === idx}>
          <button
            type="button"
            on:mouseover={() => (highlighted = idx)}
            on:focus={() => (highlighted = idx)}
            on:click={() => choose(r)}
          >
            <div class="res-main">{r.name}</div>
            {#if r.address}
              <div class="res-sub">{r.address}</div>
            {/if}
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .search-wrapper { position: relative; width: 100%; max-width: 420px; }
  .input-wrap { display: flex; align-items: center; gap: 8px; background: #fff; border-radius: 10px; padding: 6px 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid #e6e9ee; }
  .search-input { border: none; outline: none; flex: 1; font-size: 14px; padding: 8px 6px; }
  .search-input::placeholder { color: #9aa4b2; }
  .icon { width: 20px; height: 20px; color: #6b7280; }
  .clear-btn { background: transparent; border: none; color: #6b7280; cursor: pointer; font-size: 14px; padding: 4px; }

  .dropdown { position: absolute; top: calc(100% + 8px); left: 0; right: 0; background: white; border-radius: 10px; box-shadow: 0 10px 30px rgba(2,6,23,0.12); list-style: none; margin: 0; padding: 6px; z-index: 999; max-height: 260px; overflow: auto; }
  .dropdown li { padding: 4px; margin: 2px 0; }
  .dropdown li button { width: 100%; text-align: left; background: transparent; border: none; padding: 10px; border-radius: 8px; display: flex; flex-direction: column; gap: 2px; }
  .dropdown li.selected button, .dropdown li button:hover { background: linear-gradient(90deg, #eef2ff, #f8fafc); }
  .res-main { font-weight: 600; color: #0f172a; }
  .res-sub { font-size: 12px; color: #6b7280; }
</style>
