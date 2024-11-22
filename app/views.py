from typing import Any
from apl import settings
from . import models
from . import forms
from django.views.generic.edit import FormView
from django.views.generic import TemplateView,ListView,DetailView
import requests
from django.utils import timezone
import pandas as pd
import markdown


class QueryView(FormView):
    template_name = "index.html"
    form_class = forms.DifyForm

    def change_answer(self,answer):
         answer = markdown.markdown(answer,extensions=["extra"])
         return answer
    

    def get_answer_from_api(self, query,conversation_id=None):
        API_KEY = settings.API_KEY
        BASE_URL = settings.BASE_URL
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "user": "abc-123"
        }

        if conversation_id:
            data["conversation_id"] = conversation_id
        response = requests.post(BASE_URL, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            answer = response_data.get("answer","")
            conversation_id = response_data.get("conversation_id","")
            created_at = timezone.now()
            
            return answer,created_at,conversation_id
        
        else:
            return f"エラーが発生しました: {response.status_code}"
    
    
    def form_valid(self, form):
        query = form.cleaned_data['query']
        #conversation_idの取得
        conversation_id = self.request.session.get("conversation_id", None)
        #取得したconversation_idに対応するanswerを出力（メモリ機能）
        answer,created_at,conversation_id = self.get_answer_from_api(query,conversation_id)
        if conversation_id:
            self.request.session["conversation_id"] = conversation_id
        answer = self.change_answer(answer)

        query_instance = form.save(commit=False)
        query_instance.answer = answer 
        query_instance.created_at = created_at
        query_instance.conversation_id = conversation_id
        query_instance.save() 
        
        return self.render_to_response(self.get_context_data(form=form))
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation_id = self.request.session.get("conversation_id")
        if conversation_id:
            # 会話IDに関連するメッセージ履歴を取得
            context['messages'] = models.DifyModel.objects.filter(
                conversation_id=conversation_id
            ).order_by('created_at')
        else:
            # 新しい会話なら空のリスト
            context['messages'] = []
        return context
    
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    


class NewChatView(QueryView):
    def post(self, request, *args, **kwargs):
        if "conversation_id" in self.request.session:
            del self.request.session["conversation_id"]
        return self.get(request, *args, **kwargs)
    

class Memory(ListView):
    model = models.DifyModel
    template_name= "memory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = models.DifyModel.objects.all().values()
        if queryset:
            df = pd.DataFrame(queryset)
            df = df[["query","answer","created_at"]]
            df["answer"] = df["answer"].apply(lambda x:x.replace("\n",""))
            df["created_at"] = df["created_at"].apply(lambda x:str(pd.Timestamp(x).tz_convert('Asia/Tokyo')).split(".")[0])
            df = df.sort_values("created_at",ascending=False)
            df.columns = ["質問内容","回答","質問日時"]
            query = df["質問内容"].tolist()
            answer = df["回答"].tolist()
            date = df["質問日時"].tolist()
            zip_lists = zip(query,answer,date)
            context["zip_lists"] = zip_lists
            return context